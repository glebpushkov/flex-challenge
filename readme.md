### Intro

I assume that in this challenge is not expected to clarify / refine / simplify feature requirements further (unlike in the real world), to reach the goal  
"Build a **minimal** reporting application...". The most minimal / cheapest solution I see is a Serverless framework (aws lambda) + s3 bucket.
At the same, time requirements explicitly ask for a Docker file, and "Task 2" mentions upload via API.
So, I'll try to stick to the task as it is, and make some assumptions to simplify the decision process during development.
Note, there were small changes to openapi schema (added required fields and added validation for one field (but should be done for all of them)


1) According to the description I see that this system is supposed to be used internally, so **we don't expect a high load**
   (despite some batching for a daily csv upload might be nice to have, but it's also not mandatory, as file is generated at the end of the day and there is no urgency to process it as fast as possible).
2) A dashboard doesn't require the best user experience (so we can stay away from React/Angular/Vue), and no installable mobile application is expected // so we don't need to build an api for the report, and can use old and simple server rendered pages+forms, but ideally HTMX.
3) A simple cloud hosting is used to run existing infrastructure (like Digital Ocean, Hetzner..)  // so we don't use any specific cloud tools/frameworks
4) There are 2 dedicated servers - hostA (runs Web API + Dashboard) and hostB (contains a folder with CSVs and runs an app from a Task2). // imagining how task1 + task2 are deployed/used
5) In addition, I assume that CSVs may be uploaded from any other places (even work laptops), for example in case if some old CSVs have to be added to reporting database // imagining how task2 could be also used, to simplify technology selection step
6) This reporting app is not expected to grow much in terms of functionality/features

### Technologies decision

**Task 1**: as it was mentioned that it's better to do a challenge using Python, the selection was between Django(a lot of stuff out of the box, simple MVC structure, good for long living/feature reach services, monolith way), and FastAPI (which is good for building smaller / faster services). Due to simple requirements and assumption #6 I'm going to select FastAPI for that.

**Task 2**: done with Golang. As we can easily generate binaries for all platforms and could be used without docker (or even a shell?). It should be possible to run by non-dev guys to upload csvs from their workstations.

**Task 3**: Pandas! Generating of cli binary is possible, but trickier comparing to golang. Will be just wrapped in a docker.

**Task 4**: Not done...

### More details in task specific readme.md files

P.S in total it took about 2 days and 2 evenings to complete.
- (task1)learning fastAPI and the way how people structure projects / inject dependencies
- (task1)re-doing default FastAPI errors as openapi spec error, and other small obstacles which just take time
- (task3)initially tried with go & https://github.com/go-gota/gota, just to be able to ship a nice binary, but it was bad and switched to smooth&simple Pandas.
- do doing a readmes... :)

Happy reviewing! 
would be glad to hear comments about what was ok and what could be done better
