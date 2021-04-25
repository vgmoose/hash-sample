#!/bin/python3
import hashlib, time, sys, os, random, datetime

# program info
all_algos = hashlib.algorithms_guaranteed
args = sys.argv[1:]
version = "1.0.0"

# useful constants
now = datetime.datetime.now()
byte_suffixes = [ "%", "KB", "KiB", "MB", "MiB", "GB", "GiB"]
cmds = [["-h", "--help"], ["-l", "--list"], ["-a", "--algo"],
    ["-s", "--size"], ["-p", "--phrase"], ["-u", "--uniform"],
    ["-v", "--verbose"], ["-c", "--count"]]
h, l, a, s, p, u, v, c = range(8)

# term colors
bold = '\033[1m'
underline = '\033[4m'
end = '\033[0m'

def boldt(text):
    return f"{bold}{text}{end}"

# format argument info
def info(cmd, param = None, lines = []):
    short, long = cmds[cmd]
    out = f"\t{boldt(short)}, {boldt(long)}"
    if param:
        out += f" {underline}{param}{end}"
    out += "\n"
    for line in lines:
        out += f"\t\t{line}\n"
    print(out)

# defaults
algorithm = "md5"
sample_size = "1%"      # 1% of the file, for each segment
interval_count = 10     # ten segments (10% total)
seed_phrase = now.strftime('%Y-%m-%d')
use_uniform = False
use_verbose = False
files = []

def has_next(arg, xp):
    x = xp[0]
    if x + 1 >= len(args):
        print(f"Missing argument for {bold}{arg}{end}.\nSee {bold}--help{end} for more info.")
        exit(2)
    xp[0] += 1
    return args[x+1]

x = [0]
while x[0] < len(args):
    arg = args[x[0]]
    if arg in cmds[h]:
        print(f"hash-sample {version}, GPLv2+ License\n")
        print(f"{boldt('USAGE')}\n\tpython3 {underline}{sys.argv[0]}{end} [options] [file1] [file2] ...\n")
        print(f"{boldt('DESCRIPTION')}\n\tThis command will randomly sample streaks of bytes in the file to have a similar effect as hashing the full file.\n\tIt's intended to be used on large files where the speed of a \"quick check\" may be considered useful enough for file\n\tintegrity without wanting to spend time going through the entire file.\n\n\tIt should {underline}not{end} be used to guarantee every byte in the file matches, and instead used as a sanity check!\n\tThe total number of bytes read will be: {underline}sample_size{end} * {underline}interval_count{end}")
        print(f"\tWith the defaults, this will be {int(sample_size[:-1]) * interval_count}% of the total filesize ({interval_count} intervals, each {sample_size} of the file).\n")
        print(boldt("OPTIONS"))
        info(l, None, [
            "List all available algorithms on this machine separated by spaces.",
            f"These can be passed to the {bold}-a{end} flag."
        ])
        info(a, "algorithm", [
            "Specify which hashing algorithm to use during each sample.",
            f"Defaults to \"{algorithm}\""
        ])
        info(s, "sample_size", [
            "The size of each sample in bytes, or percent (of total filesize).",
            f"Can use these suffixes: {byte_suffixes}",
            f"Defaults to \"{sample_size}\""
        ])
        info(c, "interval_count", [
            f"The number of samples to take. Each will be {underline}sample_size{end} bytes.",
            f"Defaults to \"{interval_count}\""
        ])
        info(p, "seed_phrase", [
            "Any phrase or value to set the randomization seed.",
            f"Defaults to \"{seed_phrase}\" (current day)"
        ])
        info(u, None, [
            "Uniformly sample the file at equally spaced intervals instead of randomly.",
            f"Overrides any phrase provided by {bold}-p{end}."
        ])
        info(v, None, [
            "Show verbose information on the parameters and hashing for each file."
        ])
        info(h, None, ["Display this helper text."])
        print(f"Please report issues at: https://github.com/vgmoose/hash-sample\nThank you! {random.choice(['🌱','☘️']*10 + ['🍀'])}")
        exit(1)
    elif arg in cmds[l]:
        # list available algorithms
        print(" ".join(list(all_algos)))
        exit(1)
    elif arg in cmds[a]:
        algorithm = has_next(arg, x)
    elif arg in cmds[s]:
        sample_size = has_next(arg, x)
    elif arg in cmds[c]:
        interval_count = int(has_next(arg, x))
    elif arg in cmds[p]:
        seed_phrase = has_next(arg, x)
    elif arg in cmds[u]:
        use_uniform = True
    elif arg in cmds[v]:
        use_verbose = True
    else:
        # another param that wasn't an option, it should be a file
        files.append(arg)
    x[0] += 1

if use_verbose:
    print("Parameters:")
    print(f"\tAlgorithm: {algorithm}")
    print(f"\tSample Size: {sample_size}")
    print(f"\tInterval Count: {interval_count}")
    if use_uniform:
        print("\tUniform Sampling")
    else:
        print(f"\tSeed Phrase: {seed_phrase}")
    print(f"\tVersion: {version}\n")

if len(files) == 0:
    print(f"No files were specified.\nSee {bold}--help{end} for more info.")

for cur_file in files:
    try:
        with open(cur_file, "rb") as data:
            filesize = os.stat(cur_file).st_size

            # figure out how many bytes we're using for our interval size
            for x, suffix in enumerate(byte_suffixes):
                if sample_size.endswith(suffix):
                    if suffix == "%":
                        interval_size = int(filesize * (int(sample_size[:-1]) * 0.01))
                        break
                    base = (1000 + (x % 2 == 0) * 24) ** ((x+1) // 2)
                    interval_size = int(sample_size[:-len(suffix)]) * base
                    break
            else:
                # bytes directly?
                interval_size = int(sample_size)
            
            if interval_size * interval_count > filesize:
                # too much data requested
                print(f"ERROR: Too much data requested for {cur_file}. {interval_size}*{interval_count} (size*count) is {interval_size * interval_count}, which is bigger than the filesize of {filesize}")
                continue
            
            # always take the first and last interval_size bytes, regardless of anything
            intervals = [0, filesize - interval_size]
            if use_uniform:
                pass
            else:
                random.seed(seed_phrase)
                for x in range(interval_count - 2):
                    # get a random offset, see that it fits with our current set
                    for attempt in range(1):
                        repeatValue = False
                        target = random.randint(0, filesize) # we sample the full range for consistent ranges in the event of mismatched filesizes
                        for interval in intervals:
                            if repeatValue:
                                break
                            smaller, larger = min(interval, target), max(interval, target)
                            if smaller + interval_size > larger:
                                print(f"problem, {smaller}, {larger}, {smaller + interval_size}")
                                repeatValue = True
                            break
                        if repeatValue:
                            continue
                        intervals.append(target)
                        break
                    else:
                        print(f"ERROR: Hit an issue with {cur_file} when choosing partition sizes, can try a different seed phrase")
                        continue
                    intervals.sort()

            print(intervals)
            hashes = ["a"] * len(intervals)

            # file info
            if use_verbose:
                print(f"File: {cur_file}")
                print(f"\tFilesize: {filesize}")
                print(f"\tInterval Size: {interval_size}")
                for x, interval in enumerate(intervals):
                    print(f"\tsample{x+1}(start: {interval}, end: {interval + interval_size}) = {hashes[x]}")
    except FileNotFoundError as e:
        print(f"ERROR: Could not open file: \"{cur_file}\"")
