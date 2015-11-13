# pg_plural

PLProxy-based Sharding for high throughput OLAP systems.

![Shard Elephant](media/shard_elephant.png)

## Slides


```bash

npm install grunt
cd slides/reveal.js && grunt serve
```

## Ansible Automation

```bash
# Install vagrant/virtualbox somehow
cd ansible
vagrant up
ssh-add ~/.vagrant.d/insecure_private_key
cd pg_plural
ansible-playbook site.yml
```

## Generate test data and upsert it


```bash
cd ../../datagenerator
# Generate Data.
python data_generator.py

# Copy Generated Data to test machine(s).
ansible all -m copy -a \
"src=/path/to/checkout/pg_plural/datagenerator/proxy_upsert_test_counts-32-size-63-batches.sql \
dest=/tmp/proxy_upsert_test_counts-32-size-63-batches.sql" --user=vagrant

# Log into machine and execute our test data file
vagrant ssh
yes "q" | psql -d part0 -f /tmp/proxy_upsert_test_counts-32-size-63-batches.sql
```

## Verify data

```bash
psql -d part0
```

```sql
SELECT id, date, hour, category, hll_cardinality(event_ids) 
FROM proxy_dynamic_query('SELECT * FROM test_counts') 
AS (id char(22),  date date, hour smallint,  event_ids hll, category text)
ORDER BY date DESC, hour DESC, id DESC;
```

Resulting output should look like this:

```sql
           id           |    date    | hour | category | hll_cardinality 
------------------------+------------+------+----------+-----------------
 ZWJiY2ZlZDYtZTQ3NC00M2 | 2015-11-11 |   22 | bar      |               1
 ZjBkNGNjMzktYWJkMS00NW | 2015-11-11 |   22 | bar      |               1
 MzVhNmU3NjUtNDlhZC00Yj | 2015-11-11 |   22 | baz      |               1
 MzQ4YTkyMGQtY2E1ZS00ZW | 2015-11-11 |   22 | foo      |               1
 MzQ4YTkyMGQtY2E1ZS00ZW | 2015-11-11 |   22 | foo      |               1
```
