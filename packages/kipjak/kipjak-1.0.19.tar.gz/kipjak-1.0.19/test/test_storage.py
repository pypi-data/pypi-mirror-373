# test_storage.py
import kipjak as kj

#
#
def storage(self, disk_path: str=None) -> kj.StorageManifest:
	'''.'''
	if disk_path is None:
		return kj.Faulted('no storage specified.')

	m = kj.storage_manifest(disk_path)
	return m[0]

kj.bind(storage)	# Register with the framework.



if __name__ == '__main__':	# Process entry-point.
	kj.create(storage)
