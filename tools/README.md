# An API traffic simulator - simulate_api_rqsts.py
The API traffic generator/simulator, **simulate_api_rqsts.py**, helps simulate the API request load for one or more of the system’s microservices.

**simulate_api_rqsts** creates multi-threaded API requests across multiple target microservices. API HTTP requests are then sent to each microservice in parallel.

The API load is measured by requests per minute and API requests can either be uniformly or randomly paced.

The uniformly paced requests are paced out so that the time between each API call is always the same, so if we are configuring a uniformly paced load of 600 API requests/min, simulate_api_rqsts will send 1 API call every T = 100 ms.

In the randomly-paced case, each API call is sent after a random period, TR, from the time where the previous call was sent, but so that TR can never be larger or smaller than 95% of T. So if we are configuring a randomly-paced load of 600 API requests/min, TR, in that case, will be equal to a value greater than 5 ms and smaller than 195 ms.

**simulate_api_rqsts** will send 1 API call every:

(1-95%)T <= T<sub>R</sub> <= (1+95%)T (i.e., for 600 requests/min: 5 ms <= TR <= 195 ms)

$$e^{-\frac{t}{RC}}$$

The sum of all T<sub>R</sub>s, however, will still be approximately equal to the configured requests/min. In our example here, the load is 600 API requests/min.

Uniformly paced requests are better when you are manually analyzing how a particular microservice responds to the API load, while randomly paced requests are a better representation of a real-time production API request load.

# The microservices performance monitor - ms_perfmon.py
The microservices performance monitor,**ms_perfmon.py**, is another multithreading tool and is initially used for collecting and building the AI training data during the simulation period of ideal conditions.

**ms_perfmon** sends parallel API calls to each microservice in the system and then logs the API call hyperlink, the date and time at which it was sent, the receiving microservice response time, and the HTTP response code. The following is an example log entry of the collected data in a comma-separated format:

```
http://payment_ms:8080,2022-12-28 15:48:57.271370, 0.010991334915161133,200
```
Each microservice stat is collected in its own **Comma-Separated Values (CSV)** log file named after the API link itself (after cleaning up special characters). All the stat files are collected under the **perfmon_stats** directory in the ms_perfmon working path.

In real-time operation, both the PBW and PAD perform a similar job to **ms_perfmon**. They collect their own stats and measure the target microservice’s real-time performance against the baseline and the expected normal behavior.

Should we extend the MSA system’s AI capabilities by including more AI services for different purposes and use cases, which will likely require each AI service to conduct its own performance statistics collection?

Depending on the collection frequency and the type of data collected, as the number of collectors increases, scalability could become an issue. The **ms_perfmon** function, in that case, can be extended to become the main AI collector for all AI or non-AI services in the MSA system. This setup can help offload the system’s microservices and allow the MSA system to scale better.

# The response delay simulator
In ``microservices/inventory/inventory_management_ms.py``:
```python
    #Simulate a delay if received an API to do so
    if delay_max_sec > 0:
        delay_seconds = round(delay_min_sec + random.random()*(delay_max_sec-delay_min_sec), 3)
        #print("Adding a delay %s ..." %delay_seconds)
        time.sleep(delay_seconds)
        
    return ""
```
The max and min delay values can be configured using an API call. The following is an example of using curl to send an API call to configure the maximum and minimum delay response in milliseconds:
```bash
curl http://inventory_ms:8080/api/simulatedelay?min=1500&max=3500
```
Again, this feature is only for demo and test purposes. A more secure way of simulating a delay is using secured configuration files or local parameters instead.

# The API response error simulator
Similar to the response delay simulator, this feature is for demo purposes only. The API error simulator feature uses one configurable value – the average HTTP error per hour. When the feature is enabled in the microservice, the microservice will pick a randomly applicable server 500 error and respond to API requests with randomly paced responses that match the configured error rate.

The error rate can be configured using an API call. The following is an example of using ``curl`` to send an API call to configure an API error response rate of 5 HTTP errors per hour:
```bash
curl http://inventory_ms:8080/api/response_err?rate=5
```
Now, we know the testing and simulation tools available for us to use for training, testing, and simulating production for our MSA system.

In the next section, we will discuss our ABC-Intelligent-MSA operations – how to initialize the system, how to build and use training and testing data, and how to simulate the system’s production traffic.

# Building and using the training data - training_data_cleanup.py = PBW.py ?
The ms_perfmon tool will create a separate stat file for each microservice in the ``<ms_perfmon's working path>/perfmon_stats`` directory.

We recommend at least 48 hours of training data collection. Ideally, however, data should be collected with seasonality load whenever applicable. In some environments, for example, the system load may increase on weekends over weekdays, during the shopping season, and so on. These situations should be considered in the training data to be able to build a more accurate AI model.

Performance data is pulled every 10 seconds, and accordingly, with 48h of active monitoring, **ms_perfmon** produces 17,280 entries for each microservice.

Regardless of the length of the system’s training period, whenever enough performance data has been collected, the ``training_data_cleanup.py`` tool should be run to detect any outliers and sanitize the performance data before using it in our AI services.

The **training_data_cleanup** tool scrubs all the performance data files in the ``<ms_perfmon's working path>/perfmon_stats`` directory, and automatically creates a ``scrubbed_stats`` directory with all the scrubbed data for each microservice. These scrubbed files are the files that we will later use for training the AI services.

We are now ready to write our Python code for training the PBW.

Now, we have the training data and the trained model. It is time to use the model for production traffic.

In the next subsection, we will simulate production operations and describe how that can be applied to our trained MSA system, the ABC-Intelligent-MSA.

# Simulating the ABC-Intelligent-MSA’s operation
Once the system is running, the AI tools will start monitoring and collecting the microservice’s performance and trigger healing actions whenever a system problem is detected and metrics exceed the configured performance thresholds.

The production traffic is ready to be simulated now using the ``simulate_api_rqsts`` API traffic simulator and the response delay simulator function discussed earlier.

Using the API response error simulator, occasional HTTP errors can also be simulated if needed. A more sophisticated simulation would involve injecting HTTP 500 error codes as well, but we will stick to response time performance delays for simplicity.

The ``ms_perfmon`` tool will still be running to collect data for our offline analysis whenever needed.

We now need to simulate specific production use cases and see how the AI tools will respond and self-heal the entire system. In the next section, we will discuss the operations of the ``PBW`` and ``PAD`` and look into how both AI services interact with system performance readings and errors.

# Analyzing AI service operations
In the preceding sections, we started by building our first AI service and covered how to use AI to enhance the MSA system’s operations and resilience, the self-healing process, and the tools we built to generate training data and simulate the ABC-Intelligent-MSA system’s operation.

In this section, we will examine the system logs and check how the PBW and PAD interact with the system and actually enhance its operations. We will then simulate a cascading system failure and examine how the self-healing process is triggered and handled to bring the MSA system back to normal operation.

# The PBW in action
During the training period, the PBW was able to build an AI model and calculate the expected response time of each microservice in the ABC-Intelligent-MSA system. As you can see from the following log sample, under a normal system load, the average response time of the Inventory microservice is about 20 ms:

```bash
http://inventory_ms:8080,2022-11-23 15:48:25.094675, 0.01450204849243164,200
http://inventory_ms:8080,2022-11-23 15:48:35.816913, 0.0241086483001709,200
http://inventory_ms:8080,2022-11-23 15:48:46.543205, 0.02363872528076172,200
http://inventory_ms:8080,2022-11-23 15:48:57.271370, 0.010991334915161133,200
http://inventory_ms:8080,2022-11-23 15:49:07.983282, 0.021454334259033203,200
http://inventory_ms:8080,2022-11-23 15:49:18.645113, 0.012285232543945312,200
http://inventory_ms:8080,2022-11-23 15:49:29.310656, 0.0245664119720459,200
http://inventory_ms:8080,2022-11-23 15:49:40.010556, 0.013091325759887695,200
http://inventory_ms:8080,2022-11-23 15:49:50.744695, 0.021291017532348633,200
http://inventory_ms:8080,2022-11-23 15:50:01.715555, 0.024635791778564453,200
```
We configured the warning threshold for the PBW as 250 ms, and the action threshold as 750 ms. We will now start introducing an API call load to the Inventory microservice using ``simulate_api_rqsts`` and delays using the response delay simulator feature. Then, we will see how the PBW reacts from the PBW action logs.

The following are the PBW’s performance readings for about 1.5 minutes. As you can see from the readings, the response time is consistently above the 250 ms alarm threshold, but (with the exception of one reading) still below the 750 ms action threshold:

```bash
http://inventory_ms:8080,2022-11-23 18:24:00.518005, 0.6386377334594727,200
http://inventory_ms:8080,2022-11-23 18:24:11.469172, 0.7164063453674316,200
http://inventory_ms:8080,2022-11-23 18:24:22.203452, 0.7233438491821289,200
http://inventory_ms:8080,2022-11-23 18:24:32.942619, 0.7101089954376221,200
http://inventory_ms:8080,2022-11-23 18:24:43.668907, 0.6982685089111328,200
http://inventory_ms:8080,2022-11-23 18:24:54.777383, 0.8207950115203857,200
http://inventory_ms:8080,2022-11-23 18:25:05.410204, 0.6812236309051514,200
http://inventory_ms:8080,2022-11-23 18:25:16.101344, 0.6544813632965088,200
http://inventory_ms:8080,2022-11-23 18:25:27.072040, 0.7446155548095703,200
http://inventory_ms:8080,2022-11-23 18:25:37.828189, 0.6969136238098145,200
```
The readings will have to be consistently above the 750 ms action threshold for the PBW to trigger a healing action. One reading above 750 ms is not enough for an action to be triggered. However, since the readings are constantly above the 250 ms alarm threshold, the PBW is expected to trigger an alarm to the NMS/OSS system.

We need to verify the PBW’s behavior from the NMS/OSS system or the PBW’s action log. The following is a snippet of the PBW’s action log during the same period from the previous example:

```bash
2022-11-23 18:24:00.518005: Alarming high response time (0.6386377334594727) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:24:11.469172: Alarming high response time (0.7164063453674316) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:24:22.203452: Alarming high response time (0.7233438491821289) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:24:32.942619: Alarming high response time (0.7101089954376221) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:24:43.668907: Alarming high response time (0.6982685089111328) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:24:54.777383: Actionable high response time (0.8207950115203857) detected in inventory_ms. No action triggered yet.
2022-11-23 18:25:05.410204: Alarming high response time (0.6812236309051514) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:25:16.101344: Alarming high response time (0.6544813632965088) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:25:27.072040: Alarming high response time (0.7446155548095703) detected in inventory_ms. No alarm triggered yet.
2022-11-23 18:25:37.828189: Alarming high response time (0.6969136238098145) detected in inventory_ms. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-23 18:25:48.637317: Alarming high response time (0.6777710914611816) detected in inventory_ms. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-23 18:25:59.327946: Alarming high response time (0.6758050918579102) detected in inventory_ms. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-23 18:26:10.014319: Alarming high response time (0.6641242504119873) detected in inventory_ms. Yellow alarm triggered and sent to NMS/OSS system.
```
As you can see from the preceding snippet’s last 4 log entries, after a consistent delay of more than 250 ms, an alarm was triggered and sent to the NMS/OSS system. We need to increase the inventory microservice’s load and response time to see how the PBW will react.

The following is another snippet of the PBW’s performance log. Only the last 4 log entries in a series of 10 consistent response delay readings are above 750 ms:
```bash
http://inventory_ms:8080,2022-11-23 18:29:31.852330, 1.326528787612915,200
http://inventory_ms:8080,2022-11-23 18:29:43.196200, 1.4279899597167969,200
http://inventory_ms:8080,2022-11-23 18:30:05.310226, 1.0108487606048584,200
http://inventory_ms:8080,2022-11-23 18:30:16.334608, 1.1380960941314697,200
```

Normally, we would have configured all healing actions shown in ***Table 10.1***. In our demo system, however, we have configured only one healing action to demo the system self-healing operations in general. We only configured a microservice container to restart if a problem is experienced in the microservice. The response delay simulator feature is therefore a more relevant simulation tool than the other tools we have mentioned earlier.

In case of slow performance due to high API call requests volume, the most appropriate healing action would be to try to scale the microservice first and allocate more resources to respond to the high volume of API requests.

We assume in our simulation that the problem in the Inventory microservice is not necessarily due to the API request load, but rather some unforeseen problem causing the Inventory service to become unstable and unable to handle API calls promptly, so restarting the Inventory microservice could therefore fix the problem.

Now, here is a look at the PBW’s action log during the same period. Please note that prior to the actionably high response time, an alarmingly high response time below 750 ms was previously detected. The response time was higher than 250 ms and below 750 ms:

```bash
2022-11-23 18:29:31.852330: Actionable high response time (1.326528787612915) detected in inventory_ms. No action triggered yet. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-23 18:29:43.196200: Actionable high response time (1.4279899597167969) detected in inventory_ms. No action triggered yet. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-23 18:30:05.310226: Actionable high response time (1.0108487606048584) detected in inventory_ms. No action triggered yet. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-23 18:30:16.334608: Actionable high response time (1.1380960941314697) detected in inventory_ms. Red Alarm triggered and sent to NMS/OSS system.
2022-11-23 18:30:16.334608: Self-healing lock state declared for inventory_ms container.
2022-11-23 18:30:16.334608: Self-healing action triggered. Restarting inventory_ms container (inventory_management_container).
2022-11-23 18:30:21.359377: Verifying inventory_ms operations...
2022-11-23 18:30:22.945823: inventory_ms was successfully restarted
2022-11-23 18:30:23.089051: Self-healing lock state cleared for inventory_ms container.
```

As you see from the last 4 entries in the action log, the PBW detected a consistent response time (above 750 ms) and accordingly sent a red alarm to the NMS/OSS system, indicating a critical delay in the Inventory service and the need for a self-healing action to be taken. The PBW then locked the Inventory microservice to avoid clashing with healing actions from other AI services. The PBW then restarted the Inventory microservice by sending a restart API call to Docker Engine, verified that the Inventory microservice was back online, and finally unlocked the Inventory microservice.

To restart a Docker container through API, you will need to send a POST request as follows:

```bash
/containers/<container id or name>/restart
```
You can also specify the number of seconds to wait before restarting the container using a t parameter. The following is a container restart POST example to restart the Inventory service container after a 10-second wait time:

```bash
/v1.24/containers/inventory_management_container/restart?t=10
```
For more information on how to control Docker Engine using API calls, check the Docker Engine API documentation at https://docs.docker.com/engine/api/version-history/.

However, was the PBW able to fix the Inventory microservice problem?

Let’s go back now to the PBW’s performance log and see how this self-healing action impacted the Inventory service performance. The following are the log entries just before the healing action was triggered:

```bash
http://inventory_ms:8080,2022-11-23 18:30:16.334608, 0.1380960941314697,200
http://inventory_ms:8080,2022-11-23 18:30:27.629649, 0.1693825721740723,200
http://inventory_ms:8080,2022-11-23 18:30:38.486793, 0.1700718116760254,200
```

Sure enough, the response time dropped from above 1 s to a maximum of 170 ms. Not as low as it was before the problem appeared, but the Inventory microservice for sure has some breathing room now. The performance issues may very well return if the underlying problem is not attended to and properly fixed.

In a more advanced AI model, we can train and configure the system to take more sophisticated actions to fully resolve the problem whenever needed, but in this book, we are limited to a specific scope to be able to demonstrate the idea in principle and pave the way for you to develop your own AI models and algorithms for your specific use cases.

We have demonstrated in this section how the PBW works and how an action is triggered when a microservice performance issue is detected. In the following section, we will go over the PAD AI service and how the PAD takes a rather more holistic view of the entire system.

# The PAD in action
The best way to demonstrate the operations of the PAD is to simulate a cascading failure and see how the PAD can bring the MSA system back to normal operation.

To simulate a cascading failure and ensure that the PAD responds to the failure and tries to auto-heal, we will first need to disable the PBW AI service. This will prevent the PBW from triggering a healing action and prevent it from trying to resolve the problem before the PAD’s healing action(s) kick in.

Let’s quickly revisit what we have previously discussed in Chapter 3, an example of how a cascading failure happens.

As shown in ***Figure 10.5***, under heavy API traffic, a failure to the Inventory microservice could cause the ``Payment`` microservice to pile up too many API calls in the queue, waiting for a response from the Inventory service. Eventually, these API calls will consume and exhaust the available resources in the ``Payment`` microservice, causing it to fail. A failure in the ``Payment`` microservice will produce a similar situation in the Order microservice, and eventually, produce a failure for the Order microservice as well:

###### Figure 10.5: The Payment microservice is down
```mermaid
%%{init: {'theme':'forest'}}%%
flowchart LR;
          A[Order microservice]-->B[Payment microservice];
     B[Payment microservice]-->C([Inventory microservice]); 
     style C fill:#f9f,stroke:#333,stroke-width:4px
     click C "https://mermaid.js.org/syntax/flowchart.html" _blank
```

For the PAD to respond with healing actions, each of the PAD’s detected anomaly types has to have healing actions defined for it.

To successfully simulate the cascading failure, we only defined an action for a cascading failure situation. Otherwise, the PAD would automatically detect the failure in the Inventory service and self-heal it by restarting the Inventory microservice container, preventing a cascading failure from happening to begin with.

We will start by simulating a high volume of orders for the Order microservice and see how the system is going to respond to this situation in general, and specifically how the PAD will react under the situation.

To simulate a high volume of order requests, use the following ``simulate_api_rqsts`` command to target the Order microservice with a fixed uniformly paced order requests of 100,000 per minute:
```bash
simulate_api_rqsts 100000 http://order_ms:8080/place_order
```
We will now shut down the Inventory microservice and examine the PAD action logs. The following is a snippet of the log about a minute after the PAD started to detect a failure in the Inventory microservice.

Please note that we introduced sudden high-volume traffic into the system. This sudden traffic increase by itself is a traffic pattern anomaly that was picked up by the PAD, but the PAD did not respond to that specific anomaly because no healing action is specifically defined for that anomaly:
```bash
2022-11-24 11:39:13.602130: Traffic pattern anomaly detected, (inventory_ms) is likely down. No action is defined. No action triggered yet. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-24 11:39:23.469204: Traffic pattern anomaly detected, (payment_ms) slow API response detected. No action is defined. No action triggered yet.
:
:
2022-11-24 11:40:26.836405: Traffic pattern anomaly detected, (payment_ms) slow API response detected. No action is defined. No action triggered yet. Yellow alarm triggered and sent to NMS/OSS system.
```

In the preceding snippet of the PAD log, the PAD automatically recognized the Inventory service failure since no response traffic was detected from the service. However, no action was taken by the PAD since no healing action was defined for that particular anomaly. Since the anomaly was consistent for more than 1 minute, the PAD sent an alarm to the NMS/OSS system to notify the system admins of the problem.

Because of the Inventory microservice failure, the Payment microservice started to run out of resources, and the PAD picked up an unusually slow traffic flow from the Payment microservice given the API call request load applied. Accordingly, and as seen in the log, a little over 1 minute later, the PAD started to generate alarms to NMS/OSS.

As shown in the following PAD log, a few minutes after the Payment microservice anomaly, the Order microservice started acting up, and accordingly, the PAD was able to correlate all these anomalies and detect a potential cascading failure:
```bash
2022-11-24 11:47:12.450897: Traffic pattern anomaly detected, (order_ms) slow API response detected. No action is defined. No action triggered yet. Yellow alarm triggered and sent to NMS/OSS system.
2022-11-24 11:47:12.450897: Traffic pattern anomaly detected, potential cascading failure detected. No action triggered yet. Yellow alarm triggered and sent to NMS/OSS system.
```

Please note that the only microservice failure we have so far is the one we manually shut down, the Inventory microservice. Both the Payment and Order microservices are still up and running but, as it seems from the log, may be suffering from resource exhaustion.

The system is still running so far, and should the Inventory service return back online, the system will automatically recover. The user experience during the heavy load would only be slow performance during the ordering process, but no orders have been denied or failed yet.

By examining all these previously mentioned PAD action logs, and as the situation stands so far, we are still okay. However, if no action is taken to resolve the Inventory microservice problem, the system will eventually fail and user orders will start to be denied.

The short circuit traffic pattern discussed in Chapter 3 helps prevent a cascading failure from taking place, but it still cannot resolve the underlying problem. User orders in a traditional short circuit pattern implantation will still be rejected until manual intervention fixes the Inventory microservice.

That’s where the PAD comes in. Check the following PAD action log!
```bash
2022-11-24 11:48:13.638447: Traffic pattern anomaly detected, potential cascading failure detected. (inventory_ms) microservice is likely the root-cause. Red Alarm triggered and sent to NMS/OSS system.
2022-11-24 11:48:13.638447: Self-healing lock state declared for inventory_ms container.
2022-11-24 11:48:13.638447: Self-healing action triggered. Restarting inventory_ms container (inventory_management_container).
2022-11-24 11:48:18.663912: Verifying inventory_ms operations...
2022-11-24 11:48:20.325807: inventory_ms was successfully restarted
2022-11-24 11:48:20.474590: Self-healing lock state cleared for inventory_ms container.
```

The PAD was able to detect the cascading failure before it actually happened, and was able to identify the root cause of the problem. The PAD sent a red alarm to the NMS/OSS system, declared a self-healing lock state on the Inventory service to try to fix the problem’s root cause, was able to successfully restart the Inventory microservice container, and then cleared the self-healing lock on the Inventory service.

Let’s now check the microservices performance logs and ensure that the problem is fixed and that the ABC-Intelligent-MSA system and all of its microservices are running normally.

Here’s the Inventory microservice’s performance log:
```bash
http://inventory_ms:8080,2022-11-24 11:51:33.132089, 0.033451717535487,200
http://inventory_ms:8080,2022-11-24 11:51:43.894705, 0.035784934718275,200
http://inventory_ms:8080,2022-11-24 11:51:54.809743, 0.027584526453594,200
http://inventory_ms:8080,2022-11-24 11:52:06.155834, 0.028615804809435,200
```
Here’s the Payment microservice’s performance log:
```bash
http://payment_ms:8080,2022-11-24 11:54:41.109835, 0.051435877463506,200
http://payment_ms:8080,2022-11-24 11:54:51.924508, 0.102346014326819,200
http://payment_ms:8080,2022-11-24 11:55:03.372841, 0.070163827689135,200
http://payment_ms:8080,2022-11-24 11:55:14.076832, 0.157682760576845,200
```
Here’s the Order microservice’s performance log:
```bash
http://order_ms:8080,2022-11-24 11:58:37.135827, 0.209097164508914,200
http://order_ms:8080,2022-11-24 11:58:47.584731, 0.193851625041193,200
http://order_ms:8080,2022-11-24 11:58:58.243759, 0.150628069240741,200
http://order_ms:8080,2022-11-24 11:59:08.961412, 0.138192362340785,200
```
As shown for the preceding Inventory, Payment, and Order microservices, all of those microservices are back online with normal performance readings. The system is now back to normal operation and should be able to handle the production load with no issues.

# Summary
This chapter walked us through how we can build AI models to build an intelligent MSA system step by step. We accordingly built two main AI services – the PBW and the PAD – and leveraged these AI services to enhance our MSA demo system, ABC-MSA, to build an intelligent MSA system that we named ABC-Intelligent-MSA.

We explained the self-healing process design and dynamics in detail, as well as the tools we built to develop AI training data, how to simulate production operations, and how to measure the demo system’s performance. We then put the ABC-Intelligent-MSA to test, simulated a couple of use cases to demonstrate AI functions within the MSA system, and carefully examined the logs of our demo AI services to showcase the value of using AI in MSA.

Everything explained in this chapter is just an example of using AI in an MSA system. Enterprises should consider using AI services that are specifically appropriate for their own MSA system and use cases. These AI tools may very well be available through third parties or built in-house whenever needed.

In the next chapter, we will discuss the transformation process from a traditional MSA system to an intelligent MSA system – the things to consider in greenfield and brownfield implementations, and how to avoid integration challenges to make the corporate transformation as smooth as possible.
