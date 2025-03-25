REQUEST_TYPES = {
    "commitment Change": {
        "description": "A Commitment Change happens when the total loan amount or terms are modified. It involves adjusting the borrower’s credit limit or available funds based on changes in the loan agreement.",
        "sub_requests": {
            "loan increase": "A borrower requests an increase in the loan amount.",
            "loan decrease": "A borrower requests a reduction in the credit line.",
            "cashless roll": "Instead of repaying the loan, the borrower renews it under new terms"
        }
    },
    "au transfer": {
        "description": "An AU Transfer (Administrative Unit Transfer) is a reallocation of loan responsibilities between internal banking divisions or departments. It does not change loan terms or amounts but shifts who manages the loan."
    },
    "adjustment": {
        "description": "An adjustment is used to correct errors, misallocations, or unexpected changes in loan transactions. It does not change the overall loan commitment but modifies existing records to ensure accuracy."
    },
    "fee payment": {
        "description": "Covers recurring and one-time fees associated with maintaining a loan.",
        "sub_requests": {
            "ongoing fee": "Regular fees that lenders charge for loan maintenance or commitment availability.",
            "letter of redit fee": "A charge for issuing a Letter of Credit (LC), which guarantees payment to suppliers."
        }
    },
    "money movement inbound": {
        "description": "Refers to funds coming into the bank for loan repayment or related payments.",
        "sub_requests": {
            "principal": "The borrower repays the loan's original amount.",
            "interest": "Borrowers pay only the interest due on a loan.",
            "principal+interest": "A borrower repays both principal and interest together.",
            "principal+interest+fee": "Loan payment that includes other service fees in addition to principal and interest."
        }
    },
    "money movement outbound": {
        "description": "Funds moving out of the bank for loan disbursements, foreign transactions, or scheduled payments.",
        "sub_requests": {
            "timebound": "Payments that must be processed within a strict time frame.",
            "foreign currency": "Payments requiring currency exchange."
        }
    },
    "closing notice": {
        "description": "A closing notice is an official communication that marks the closing or finalization of a loan transaction. It often includes information about principal amounts, fees, and any required adjustments.",
        "sub_requests": {
            "reallocation fees": "When the loan’s exposure is redistributed among lenders in a syndicated loan.",
            "amendment fees": "Charges applied when the terms of a loan agreement are modified.",
            "reallocation principal": "Adjusting how the principal balance is distributed among lenders in a syndicated loan agreement."
        }
    }
}

ROLE="Commercial Bank Lending Service teams receive a significant volume of servicing requests through emails. These emails contain diverse requests, often with attachments and will be ingested to the loan servicing platform and creates service requests which will go through the workflow processing. You are a system whose role is classify these email contents into either of the request and sub request types. The output expected is expected in the json format that can be easily parsed by a json parser.These are the field names that should be present in the json response {request_type,sub_request_type,confidence_score}.Here request_type and sub_request_type should match any from the below mentioned list and confidence score is the confidence of classification. Apart from this extract any important data mentioned in the email and add them into the json response as well. Different request types and sub request types with their descriptions are here -"
