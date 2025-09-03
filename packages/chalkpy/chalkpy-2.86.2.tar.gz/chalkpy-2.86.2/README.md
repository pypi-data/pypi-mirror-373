# Chalk

Chalk enables innovative machine learning teams to focus on building
the unique products and models that make their business stand out.
Behind the scenes Chalk seamlessly handles data infrastructure with
a best-in-class developer experience. Here’s how it works –

---

## Develop

Chalk makes it simple to develop feature pipelines for machine
learning. Define Python functions using the libraries and tools you're
familiar with instead of specialized DSLs. Chalk then orchestrates
your functions into pipelines that execute in parallel on a Rust-based
engine and coordinates the infrastructure required to compute
features.

### Features

To get started, [define your features](/docs/features) with
[Pydantic](https://pydantic-docs.helpmanual.io/)-inspired Python classes.
You can define schemas, specify relationships, and add metadata
to help your team share and re-use work.

```py
@features
class User:
    id: int
    full_name: str
    nickname: Optional[str]
    email: Optional[str]
    birthday: date
    credit_score: float
    datawarehouse_feature: float

    transactions: DataFrame[Transaction] = has_many(lambda: Transaction.user_id == User.id)
```

### Resolvers

Next, tell Chalk how to compute your features.
Chalk ingests data from your existing data stores,
and lets you use Python to compute features with
[feature resolvers](/docs/resolver-overview).
Feature resolvers are declared with the decorators `@online` and
`@offline`, and can depend on the outputs of other feature resolvers.

Resolvers make it easy to rapidly integrate a wide variety of data
sources, join them together, and use them in your model.

#### SQL

```python
pg = PostgreSQLSource()

@online
def get_user(uid: User.id) -> Features[User.full_name, User.email]:
    return pg.query_string(
        "select email, full_name from users where id=:id",
        args=dict(id=uid)
    ).one()
```

#### REST

```python
import requests

@online
def get_socure_score(uid: User.id) -> Features[User.socure_score]:
    return (
        requests.get("https://api.socure.com", json={
            id: uid
        }).json()['socure_score']
    )
```

---

## Execute

Once you've defined your features and resolvers, Chalk orchestrates
them into flexible pipelines that make training and executing models easy.

Chalk has built-in support for feature engineering workflows --
no need to manage Airflow or orchestrate complicated streaming flows.
You can execute resolver pipelines with declarative caching,
ingest batch data on a schedule, and easily make slow sources
available online for low-latency serving.

### Caching

Many data sources (like vendor APIs) are too slow for online use cases
and/or charge a high dollar cost-per-call. Chalk lets you optimize latency
and cost by defining declarative caching policies which are well-integrated
throughout the system. You no longer have to manage Redis, Memcached, DynamodDB,
or spend time tuning cache-warming pipelines.

Add a caching policy with one line of code in your feature definition:

```python
@features
class ExternalBankAccount:
-   balance: int
+   balance: int = feature(max_staleness="**1d**")
```

Optionally warm feature caches by executing resolvers on a schedule:

```py
@online(cron="**1d**")
def fn(id: User.id) -> User.credit_score:
  return redshift.query(...).all()
```

Or override staleness tolerances at query time when you need fresher
data for your models:

```py
chalk.query(
    ...,
    outputs=[User.fraud_score],
    max_staleness={User.fraud_score: "1m"}
)
```

### Batch ETL ingestion

Chalk also makes it simple to generate training sets from data warehouse
sources -- join data from services like S3, Redshift, BQ, Snowflake
(or other custom sources) with historical features computed online.
Specify a cron schedule on an `@offline` resolver and Chalk automatically ingests
data with support for incremental reads:

```py
@offline(cron="**1h**")
def fn() -> Feature[User.id, User.datawarehouse_feature]:
  return redshift.query(...).incremental()
```

Chalk makes this data available for point-in-time-correct dataset
generation for data science use-cases. Every pipeline has built-in
monitoring and alerting to ensure data quality and timeliness.

### Reverse ETL

When your model needs to use features that are canonically stored in
a high-latency data source (like a data warehouse), Chalk's Reverse
ETL support makes it simple to bring those features online and serve
them quickly.

Add a single line of code to an `offline` resolver, and Chalk constructs
a managed reverse ETL pipeline for that data source:

```py
@offline(offline_to_online_etl="5m")
```

Now data from slow offline data sources is automatically available for
low-latency online serving.

---

## Deploy + query

Once you've defined your pipelines, you can rapidly deploy them to
production with Chalk's CLI:

```bash
chalk apply
```

This creates a deployment of your project, which is served at a unique
preview URL. You can promote this deployment to production, or
perform QA workflows on your preview environment to make sure that
your Chalk deployment performs as expected.

Once you promote your deployment to production, Chalk makes features
available for low-latency [online inference](/docs/query-basics) and
[offline training](/docs/query-offline). Significantly, Chalk uses
the exact same source code to serve temporally-consistent training
sets to data scientists and live feature values to models. This re-use
ensures that feature values from online and offline contexts match and
dramatically cuts development time.

### Online inference

Chalk's online store & feature computation engine make it easy to query
features with ultra low-latency, so you can use your feature pipelines
to serve online inference use-cases.

Integrating Chalk with your production application takes minutes via
Chalk's simple REST API:

```python
result = ChalkClient().query(
    input={
        User.name: "Katherine Johnson"
    },
    output=[User.fico_score],
    staleness={User.fico_score: "10m"},
)
result.get_feature_value(User.fico_score)
```

Features computed to serve online requests are also replicated to Chalk's
offline store for historical performance tracking and training set generation.

### Offline training

Data scientists can use Chalk's Jupyter integration to create datasets
and train models. Datasets are stored and tracked so that they can be
re-used by other modelers, and so that model provenance is tracked for
audit and reproducibility.

```python
X = ChalkClient.offline_query(
    input=labels[[User.uid, timestamp]],
    output=[
        User.returned_transactions_last_60,
        User.user_account_name_match_score,
        User.socure_score,
        User.identity.has_verified_phone,
        User.identity.is_voip_phone,
        User.identity.account_age_days,
        User.identity.email_age,
    ],
)
```

Chalk datasets are always "temporally consistent."
This means that you can provide labels with different past timestamps and
get historical features that represent what your application would have
retrieved online at those past times. Temporal consistency ensures that
your model training doesn't mix "future" and "past" data.
