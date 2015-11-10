from data_generator import PgDataGenerator

NUM_ROWS = 2000
BATCH_SIZES = [4, 8, 32, 128, 512] # 1024, 2048]
NUM_BATCHES = [
	int(round(NUM_ROWS/float(batch_size))) for batch_size in BATCH_SIZES
]

# Test specific stuff
# TODO(gavin) make this read ansible data to construct the base template.
FUNCTION_NAME = 'proxy_upsert_test_counts'
OUT_FILE_NAME_TEMPL = "{0}-{1}-size-{2}-batches.sql"

SQL_TEMPL = ("select {0}('{{{1}}}'::text[], '{{{2}}}'::date[], '{{{3}}}'"
			 "::smallint[], '{{{4}}}'::text[], '{{{5}}}'::text[]);")


def _make_batch_sql(func_name, ids, dates, hours, event_ids, categories):
	"""
	 Example output looks like this:
	select test_counts(
		'{aaa,aaa,aaa}'::text[],
		'{2015-05-15,2015-05-16,2015-05-16}'::date[],
		'{20,21,23}'::smallint[],
		'{cabef32d,cabef32f,deadbeef1}'::text[],
		'{Foo,Bar,Foo}'::text[]);
	"""
	return SQL_TEMPL.format(
			func_name,
            ','.join(ids),
            ','.join(dates),
            ','.join(hours),
            ','.join(event_ids),
            ','.join(categories)
    )


def main():
    daters = PgDataGenerator()
    for i in range(0, len(BATCH_SIZES)):
        with open(OUT_FILE_NAME_TEMPL.format(
			FUNCTION_NAME, BATCH_SIZES[i], NUM_BATCHES[i]), 'w') as sql:
            for batch in range(0, NUM_BATCHES[i]):
                ids = []
                dates = []
                hours = []
                event_ids = []
                categories = []
                for datum in range(0, BATCH_SIZES[i]):
                    micro_batch = daters.process_dims()
                    ids.append(micro_batch['ids'])
                    dates.append(micro_batch['date'])
                    hours.append(str(micro_batch['hour']))
                    event_ids.append(micro_batch['event_ids'] or 'null')
                    categories.append(micro_batch['categories'])

                sql.write(_make_batch_sql(
					FUNCTION_NAME, ids, dates, hours, event_ids, categories))
                sql.write('\n')


if __name__ == '__main__':
    main()
