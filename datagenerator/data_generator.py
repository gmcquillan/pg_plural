import base64
import random
import time
import uuid

from collections import OrderedDict
from datetime import datetime, timedelta
from functools import wraps

 
def return_percent(percent):

    def decorator(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            if (random.randint(0, 100) > percent):
                return None

            return func(*args, **kwargs) 

        return _wrapped 

    return decorator


def timeit(func):
    def _wrapped(*args, **kwargs):
        ts = time.time() * 1000
        results = func(*args, **kwargs)
        te = time.time() * 1000

        print('{!r} ({!r}, {!r}) {.4}ms'.format(
            func.__name__, args, kwargs, te-ts))

        return results

    return _wrapped


class PgDataGenerator(object):

    def __init__(self, num_apps=10, max_events=10):
        self.num_apps = num_apps
        self.max_events = max_events
        # Lowest resolution is hours.
        # We create a bucket placeholder equal to the amount of time
        # we want to simulate for our counters.
        self.num_buckets = 24 # One day's worth of deltas.

        self.dims = OrderedDict([
            ('date',  self.get_date),
            ('hour',  self.get_hour),
            ('ids', self.get_id),
            ('event_ids', self.get_uuid),
            ('categories', self.get_category)
        ])

        # This is weird, but a way of keeping data 
		# consistent between runs if we choose to.
        try:
            import id_data

            self.ids = id_data.IDS
            self.event_ids = id_data.EVENT_IDS

        except ImportError:
            self.ids = [
				base64.b64encode(str(uuid.uuid4()))[0:22] 
				for x in range (0, num_apps)
			]
            # many pushIds should be able to map to one appKey
            # app-key -> [list of event_ids]
            self.event_ids = self._gen_event_ids()

        # Likewise many event_ids should map to one groupId
        # Fornow we'll have an inverted look up of pushId -> groupId.

        self.deltas = [timedelta(hours=x) for x in range(1, self.num_buckets)]
        self.categories = ['foo', 'bar', 'baz']

    def _get_id_data_str(self):
        return ''.join(
            ['IDS =', unicode(self.ids), '\n',
			 'EVENT_IDS =', unicode(self.event_ids)]) 

    def serialize_id_data(self):
        with open('id_data.py', 'w') as id_data_file:
            id_data_file.write(self._get_id_data_str)

    def get_date(self, *args):
        date = datetime.utcnow() - random.choice(self.deltas)
        return date.isoformat().split('T')[0]

    def get_hour(self, *args):
        return random.choice(range(0, 23))

    def get_id(self, *args):
        if args:
            return args[0]
        return random.choice(self.ids)

    def get_uuid(self, *args):
        return str(uuid.uuid4())

    def get_category(self, *args):
        return random.choice(self.categories)

    # Needs to be run before get_event_ids is run
    def _gen_event_ids(self):
        return {
			id: [str(uuid.uuid4()) for x in range(
					0, random.randint(1, self.max_events))
				]
            	for id in self.ids
		}


    @return_percent(75)
    def get_event_id(self, *args):
        id = args[0]
        # Return a random push id, from an id's list.
        return random.choice(self.event_ids[id])

    def process_dims(self):
        id = self.get_id()
        return {dim: self.dims[dim](id) for dim in self.dims}

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
