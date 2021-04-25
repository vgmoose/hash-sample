# hash-sample
Sample and hash sections of very large files to compare without going through entire file

```

USAGE
	python3 hashsample.py [options] [file1] [file2] ...

DESCRIPTION
	This command will randomly sample streaks of bytes in the file to have a similar effect as hashing the full file.
	It's intended to be used on large files where the speed of a "quick check" may be considered useful enough for file
	integrity without wanting to spend time going through the entire file.

	It should not be used to guarantee every byte in the file matches, and instead used as a sanity check!
	The total number of bytes read will be: sample_size * interval_count
	With the defaults, this will be 20% of the total filesize (20 intervals, each 1% of the file).

OPTIONS
	-l, --list
		List all available algorithms on this machine separated by spaces.
		These can be passed to the -a flag.

	-a, --algo algorithm
		Specify which hashing algorithm to use during each sample.
		Defaults to "sha3_512"

	-s, --size sample_size
		The size of each sample in bytes, or percent (of total filesize).
		Can use these suffixes: ['%', 'KB', 'KiB', 'MB', 'MiB', 'GB', 'GiB']
		Defaults to "1%"

	-c, --count interval_count
		The number of samples to take. Each will be sample_size bytes.
		Defaults to "20"

	-p, --phrase seed_phrase
		Any phrase or value to set the randomization seed.
		Defaults to "2021-04-24" (current day)

	-v, --verbose
		Show verbose information on the parameters and hashing for each file.

	-h, --help
		Display this helper text.
```
