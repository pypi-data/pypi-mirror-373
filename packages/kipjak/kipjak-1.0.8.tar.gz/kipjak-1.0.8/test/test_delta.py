# test_storage.py
import kipjak as kj

#
#
def delta(self, left_path: str=None, right_path: str=None) -> list[kj.Any]:
	'''.'''
	if left_path is None or right_path is None:
		return kj.Faulted('no storage specified.')

	lp = kj.storage_manifest(left_path)
	rp = kj.storage_manifest(right_path)

	m = [d for d in kj.storage_delta(lp[0], rp[0])]

	return m

kj.bind(delta)	# Register with the framework.



if __name__ == '__main__':	# Process entry-point.
	kj.create(delta)
