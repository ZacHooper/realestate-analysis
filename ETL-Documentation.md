# The realestate analysis ETL

This ETL pipeline is to query, process and store new listings for given postcodes from Domain.com.au. The postcodes are for places located around where I live as that are the listings I'm interested in for later analysis.

## Limitations
There are some limitations with the services that I'm working with. I don't envision getting close to them but it is good to be aware.
- Only allowed 500 requests to Domain a day
- Only allowed 10000 Prefect tasks a month (should be fine)

## Why use Prefect as Orchestrator
Prefect is an orchestrator, focused on writing ETL pipelines with Python. I've chosen Prefect over other orchestrators, such as Airflow, for it's better compatibility with Python and easier deployment methods. 

### Oversight & Management
By adding the complexity of Prefect to the ETL process it provides greater management and oversight. I can see how all the processes in the ETL pipeline fit together, when it's scheduled to run and any errors that occurred in past runs. 

I can manage many of the awkward tasks, such as scheduling and troubleshooting through a UI rather than trawling through a console on a VM. 

### Troubleshooting
Prefect provides great insight into when and where any errors occurred. It also guides you to write your ETL pipeline in a way that should an error occur all steps prior to the error should still complete. For example, if there was an error in my transformation step all the raw data form the Extract step would still be uploaded allowing me to retroactively finish the ETL once the bug was fixed. 

### Easier Deployment
By using Prefect, in conjunction with Docker I can deploy my ETL pipeline into production much easier and technically on any hardware. With it's agents I can spin up and VM with a Prefect Docker Agent and have my ETL script run. It's not required for this ETL pipeline (yet) but this would allow me to easily scale up the production with ease. It could also facilitate a distributed architecture like Kubernetes if it was required. 

### Example Dashboard
Here is an example of the dashboard you see when you login. Clearly I've got some debugging to do with the script. 
![Screenshot 2021-11-09 at 16 19 55](https://user-images.githubusercontent.com/19284719/140870760-1da630df-c5c2-4498-ab7b-8fe120286027.png)

## Why MongoDB
The simplest answer is the free tier is good.

However, using a NoSQL / Document database gives me the flexibility to change the schema of my data as the project grows and evolves overtime. I expect to add new information to new documents in the future making it more practical to use the MongoDB. 

I can also upload the data in a tabular way (object with no nested data) for essentially classic RDBS usage if and when required. 


## The Pipeline

The goal of the pipeline is to get all new listings from Domain.com.au for given postcodes.

The steps to do this are:
1. Get "todays" listings from Domain in the postcodes provided
2. Upload the raw result to MongoDB
3. Compare the listings already in MongoDB to today's listings and determine any new listings
4. Get the full listing details from Domain for any new listings
5. Transform the listing details
    - dropping unnecessary fields
    - extracting specific data from text fields
    - Basic pre-processing to clean the data as much as possible for analysis
6. Upload new listing to MongoDB

### 1. Get "todays" listings from Domain in the postcodes provided

By querying the `POST /v1/listings/residential/_search/` endpoint from the Domain API with the at least the following parameters: `postcode` & `listingType`, I can get all of current listings for today. 

This is possibly the easiest part of the ETL process as all it requires is a request to the Domain API. I do make a check to see if there's any extra pages requiring a subsequent request.

### 2. Upload the raw result to MongoDB

I'm uploading the returned raw data to MongoDB to facilitate better troubleshooting capabilities and retroactive analysis. 

#### Troubleshooting
If something goes wrong downstream I can look at the exact data I received from Domain originally. This may help to solve the problem or manually input data if required. 

#### Retroactive Analysis
If in the future I decide I want to analysis something that I can no longer query from the Domain API I will have the data stored for all the listings in my database.

### 3. Compare the listings already in MongoDB to today's listings and determine any new listings

So not create any duplicates in the database and be a good user of the Domain API I want to make sure I'm only getting the full listing information for listings not already in my MongoDB. 

The process for this is to query the DB for all the listing ids. I then compare today's listing ids with the DBs list, any ids not in the DBs list must be new. I discard all the existing ids and continue the ETL process with the new listings. 

### 4. Get the full listing details from Domain for any new listings

By querying the `GET /v1/listings/{id}/` endpoint I can get all the information about a listing. The data from the original query contains a lot of information but fields such as `description` may be shortened to not contain the full text. By querying for the listing specifically I can get the full text. 

This is a simple loop over the new listing ids identified in step 3. 

### 5. Transform the listing details

The listing data returned is not guaranteed to be clean as I expect the original data was entered by the agent trying to sell the property. A great example is the price field is often never whilst the `displayPrice` will also contain unexpected text such as `AUCTION: $1,000,000 - $1,200,000` or `CONTACT AGENT`. If the price is present in the display price field we need to extract it into numerical fields so that it can be used. 

Additionally, in this step we can do a lot of the pre-processing required for analysis such as handling white space in text, removing superfluous fields, making sure the data adheres to tidy principles, etc. 

To make later analysis easier I'm ensuring this transformed data has no nested objects so that it can easily be downloaded into a tabular format. 

### 6. Upload new listing to MongoDB
Once the new listing has been transformed it get's uploaded to MongoDB

## Future Goals
The basic structure of the ETL process is unlikely to change too much, however, further transformation may be undertaken on the listings before being uploaded. These extra transformation include:
- Calculating the distance to the beach
- Calculating the distance to a supermarket
- NLP of the description to extract important information
- OCR of the statement of information to extract house price when not provided on listing

The only change to the process that I envision will occur is the addition of checking whether a listing as been sold and if so, for how much. I'm still debating whether this should be added into this ETL or whether another ETL pipeline will be created to run on a different schedule checking if listings have been sold or not. 
