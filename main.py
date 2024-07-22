import base64
import json
import requests
from fastapi import FastAPI, Query
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

class filterAndPromptGPT_request(BaseModel):
    prompt: str

# Global Variables
unqork_credentials = "uqd7c92eb4-cb56-4de1-90ad-092d69375383:,zM@EvxpN*<-d62(q30[o5))1eiJHMYA"
encoded_credentials = base64.b64encode(unqork_credentials.encode('utf-8')).decode('utf-8')

OpenAI = OpenAI(
    api_key = "sk-None-Z5F55HIvccxIF8hk1lsOT3BlbkFJDyKbHHS07JShbmId8S94"
)

dbSchema = '{"data.clientName": {"type": "String","description": "Name of the client"},"data.clientType": {"type": "String","description": "Type of client (e.g., Trust, LLC)"},"data.states": {"type": "String","description": "Current state of the record (if applicable)"},"data.documentName": {"type": "String","description": "Name of the document associated with the agreement"},"data.endDate": {"type": "String","description": "End date of the agreement"},"data.documentType": {"type": "String","description": "Type of agreement (e.g., NDA, ISDA, CSA)"},"data.attributesData": {"type": "Object","description": "Details specific to the agreement","properties": {"Name of Client": {"type": "String","description": "Name of the client involved in the agreement"},"Type of Agreement": {"type": "String","description": "Type or title of the agreement"},"Date of Agreement": {"type": "String","description": "Date when the agreement was executed"},"Eligible Collateral": {"type": "String","description": "Description of eligible collateral (if applicable)"},"Notification Time": {"type": "String","description": "Time of notification specified in the agreement"},"Transfer Timing": {"type": "String","description": "Timing for transfer as per the agreement"},"Valuation Date": {"type": "String","description": "Date for valuation (if specified)"},"Valuation Time": {"type": "String","description": "Time for valuation (if specified)"},"Governing Law of Agreement": {"type": "String","description": "Jurisdiction or governing law of the agreement"},"End Date of Agreement": {"type": "String","description": "End date of the agreement term"},"Valuation Agent": {"type": "String","description": "Entity designated as the valuation agent"},"Minimum Net Asset Value Event": {"type": "String","description": "Applicability of Minimum Net Asset Value Event"},"Failure to Deliver Statement of Net Asset Value": {"type": "String","description": "Applicability of Failure to Deliver Statement of Net Asset Value"},"Change in Law": {"type": "String","description": "Applicability of Change in Law"},"Regulatory Event": {"type": "String","description": "Applicability of Regulatory Event"},"Government Action Event": {"type": "String","description": "Applicability of Government Action Event"},"Investment Manager Event": {"type": "String","description": "Applicability of Investment Manager Event"}}},"data.qunsResponse": {"type": "Object","description": "Additional details related to the agreement","properties": {"What are the Thresholds in Paragraph 13?": {"type": "String","description": "Details about thresholds specified in Paragraph 13"},"What is the Resolution Time?": {"type": "String","description": "Resolution time specified in the agreement"},"What is defined as “Eligible Collateral”?": {"type": "String","description": "Definition or description of eligible collateral"},"What is the Minimum Transfer Amount?": {"type": "String","description": "Minimum transfer amount specified in the agreement"},"Who is identified as Valuation Agent?": {"type": "String","description": "Entity identified as the valuation agent"},"What is the Valuation Time?": {"type": "String","description": "Valuation time specified in the agreement"},"What is the Valuation Date Location for Party A and Party B?": {"type": "String","description": "Location specified for valuation date for both parties"},"What Condition Precedents are elected in the CSA?": {"type": "String","description": "Condition precedents elected as per the agreement"},"Is Paragraph 7 amended to delete “two (2) Business Days”?": {"type": "String","description": "Specification whether Paragraph 7 is amended"},"Are interest payments applicable?": {"type": "String","description": "Applicability of interest payments"},"Is rehypothecation applicable to both Party A and Party B? In the VM CSA this is under Paragraph 13(h)(ii).": {"type": "String","description": "Applicability of rehypothecation as per Paragraph 13(h)(ii)"},"Notification Time provision is found in Paragraph 13(d)(iv) of the VM CSA?": {"type": "String","description": "Specification of notification time provision in Paragraph 13(d)(iv)"},"Are the Additional Termination Events applicable to Party A or Party B or Party A and Party B?": {"type": "String","description": "Applicability of additional termination events"},"What are the Decline in Net Asset Value triggers under Part 1(g)(iv)?": {"type": "String","description": "Triggers for decline in net asset value under Part 1(g)(iv)"},"What is the Minimum Net Asset Value Event/Minimum Total Equity Floor under Part 1(g)(v)?": {"type": "String","description": "Specification of Minimum Net Asset Value Event/Minimum Total Equity Floor"},"Does the ISDA reference NAV or Total Equity for Party B?": {"type": "String","description": "Reference to NAV or Total Equity for Party B"},"What is the Cross Default Threshold Amount for Party A and Party B?": {"type": "String","description": "Cross Default Threshold Amount for Party A and Party B"},"Is Credit Event Upon Merger applicable to Party A and Party B?": {"type": "String","description": "Applicability of Credit Event Upon Merger"},"Does the Confirmation Procedure provision reference 24 hours?": {"type": "String","description": "Specification whether Confirmation Procedure provision references 24 hours"},"Who is the Credit Support Provider for Party A?": {"type": "String","description": "Entity identified as the credit support provider for Party A"},"What is the governing law of this agreement?": {"type": "String","description": "Jurisdiction or governing law of the agreement"},"What is the date of this NDA?": {"type": "String","description": "Date of the NDA"},"Is the Material Non-Public Information clause in the agreement?": {"type": "String","description": "Applicability of Material Non-Public Information clause"},"What is the jurisdiction for the NDA?": {"type": "String","description": "Jurisdiction specified for the NDA"},"Is there a non-solicitation provision in the agreement?": {"type": "String","description": "Specification of non-solicitation provision in the agreement"},"Is there a “Representatives” provision in the NDA?": {"type": "String","description": "Specification of Representatives provision in the NDA"},"Is the NDA bilateral (mutual) or unilateral?": {"type": "String","description": "Type of NDA (bilateral or unilateral)"}}}}';

async def getUnqorkBearerToken():
    headers = {"Authorization": "Basic " + encoded_credentials,"Content-Type": "application/json"}
    request_body={"grant_type": "client_credentials"}
    response = requests.post("https://aiden-ai-staging.unqork.io/api/1.0/oauth2/access_token", headers=headers, json=request_body)
    return response.json().get('access_token')


async def getFilterQuery(prompt):
    response = OpenAI.chat.completions.create(
    model="gpt-4o",
    response_format={ "type": "json_object" },
    messages=[
      {"role": "system", "content": 'Provided by the assistant is a Schema of MongoDB collection, Your task is to generate a very simple MongoDB query like {"data.client": "Steffy"} that retrieves records from the DB that are relevant to the user prompt, respond in JSON format.'},
      {"role": "assistant", "content": dbSchema},
      {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content

async def getFilteredDBRecords(bearerToken, filterQuery):
    headers = {"Authorization": "Bearer " + bearerToken,"Content-Type": "application/json"}
    request_body = {"filterQuery": filterQuery}
    response = requests.post("https://aiden-ai-staging.unqork.io/fbu/uapi/modules/6698dd862052457ea025dfb2/api", headers=headers, json=request_body)

    if(response.status_code != 200): return []
    return response.json().get('data').get('resolved').get('filteredData')

async def promptLLM(prompt, context):
    response = OpenAI.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "system", "content": "You are provided some MongoDB records as context, based on those records respond to user query, appologise if the context doesnt contain any relevent data, Do not use markdown formatting in response"},
      {"role": "assistant", "content": json.dumps(context)},
      {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content


@app.get("/filter-and-prompt-gpt")
async def filterAndPromptGPT(
    prompt: str = Query(..., description="The prompt for querying"),
):
    try:
        tries = 0
        filteredDBRecords = []
        filterQuery = ""
        
        while len(filteredDBRecords) == 0 and tries < 5:
            print(f"Try #{tries}")
            tries += 1
            filterQuery = await getFilterQuery(f"{prompt} {f'{filterQuery} is a wrong query' if tries > 1 else ''}")
            print(f"Received filter query: {filterQuery}")
            unqork_bearerToken = await getUnqorkBearerToken()
            filteredDBRecords = await getFilteredDBRecords(unqork_bearerToken, filterQuery)
            print(f"Received {len(filteredDBRecords)} records")
        
        if len(filteredDBRecords) == 0:
            return {"response": "Sorry, I couldn't find specific data relevant to your query. Please try rephrasing your question to focus on column names or provide more specific details."}
        else:
            llm_response = await promptLLM(prompt, filteredDBRecords)
            return {"response": llm_response}
    
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/health")
async def health():
    return {"response": "i m alive"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7001)
    allow_origin