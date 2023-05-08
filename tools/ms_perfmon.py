import sys, os, asyncio, aiohttp, datetime, time
from pathlib import Path

build_no = "0.1"
usage_help = """
        Usage:
            simulate_api_rqsts --version | --help | <pull interval> <url list file> [-v]
            
        Where:
            --version: Shows the current release/build version
            
            --help: shows this message
            
            pull interval: Time in seconds between each service's stats pull request
            
            url list file: Is the text file with a list of all target URLs where the API calls will be sent to
                 Have each target URL in a separate line
                            
            -v: Verbose mode
"""

show_version_output = "\nms_perfmon ver. %s\n" % build_no

if len(sys.argv) <= 1:
    print("ERROR: Missing parameters")
    print(show_version_output)
    print(usage_help)
    sys.exit(-1)


#Initialize Params
REQ_TIMEOUT = 3
verbose = '-v' in sys.argv

if '--help' in sys.argv:
    print(show_version_output)
    print(usage_help)
    sys.exit(0)

if '--version' in sys.argv:
    print(show_version_output)
    sys.exit(0)

pull_interval = sys.argv[1]
if pull_interval.isnumeric():
    pull_interval = int(pull_interval)
    if pull_interval<=0:
        print("ERROR: Stats pull interval needs to be a number > 0s")
        sys.exit(-1)

    url_list = []
    if len(sys.argv) > 2:
        tmp = sys.argv[2];
        if "http" in tmp:
            url_list.append(tmp);
        else:    
            url_list_file = open(tmp, "r");
            for url in url_list_file:
                url_list.append(url)

else:
    print("ERROR: API Calls Rate needs to be an integer")
    sys.exit(-1)
        

def create_url_filename(url):
    filename = url.replace("http://", "")
    filename = url.replace("https://", "")
    filename = filename.replace(":", "_")
    filename = filename.replace("/", "_")
    filename = filename.replace("\n", "")
    return filename

async def get(url, session):
    #to get the current working directory
    directory = os.getcwd()
    # print("---------------------------------------")
    # print(directory)
    if not os.path.exists(directory+"/perfmon_stats"):
       os.makedirs(directory+"/perfmon_stats")

    try:
        request_datetime = str(datetime.datetime.now())
        start_time = time.time()
        async with session.get(url=url, timeout=REQ_TIMEOUT) as response:
            resp = await response.read()
            end_time = time.time()
            response_status_code = response.status
            response_total_seconds = str(end_time-start_time)
            
            filename = directory+"/perfmon_stats/" + create_url_filename(url) + ".csv"
            file_exists = os.path.isfile(filename)
            if file_exists:
                f = open(filename, "a")                
            else:
                Path(filename).touch() 
                f = open(filename, "w")
                f.write("url,request_datetime,response_time,status_code\n")

            f.write("%s,%s,%s,%s\n" %(url, request_datetime, response_total_seconds, response_status_code) )
            f.close()
            
    except Exception as e:
        filename = directory+"/perfmon_stats/" + create_url_filename(url) + ".csv"
        file_exists = os.path.isfile(filename)
        if file_exists:
            f = open(filename, "a")                
        else:
            Path(filename).touch() 
            f = open(filename, "w")
            f.write("url,request_datetime,response_time\n")

        f.write("%s,%s,%s,%s\n" %(url, request_datetime, 0, "ClientConnectorError") )
        f.close()


async def main(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])

if verbose:
    print("Pulling stats for the following URL List:")
    print(url_list)

n = 1
while True:
    if verbose:
        print("Stats pull request... #"+ str(n))
        n = n+1
    
    asyncio.run(main(url_list))
    time.sleep(pull_interval)
