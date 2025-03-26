# 🚀 LoanAI Classifier

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
Banks and financial institutions receive thousands of loan service request emails daily. These emails require manual classification, leading to inefficiencies, delays, and errors. Common challenges include:

- **Manual Processing Delays**: Loan officers spend hours sorting and responding to emails, delaying critical loan processing tasks.
- **High Error Rate in Categorization**: Misclassification can lead to delays in approvals and compliance risks.
- **Scalability Issues**: As the volume of loan requests grows, manual processing becomes increasingly unsustainable.

## Solution
This AI-powered system automates loan request classification by:

- ✅ **Automating Email Processing** → Extracting loan request types, key attributes, and relevant details from emails & attachments.
- ✅ **Enhancing Accuracy** → Utilizing LLM-based classification to improve precision in sorting loan-related emails.
- ✅ **Speeding Up Response Time** → Enabling near-instant classification and forwarding to the right department.
- ✅ **Seamless Integration** → Connecting with CRM & Loan Management Systems via API for structured data output.
## 🎥 Demo

🔗 [Live Demo](https://drive.google.com/file/d/1cJzaQUNahjcg7BDnBrRkcf41yieNA4_e/view?usp=sharing)   
📹 [Video Demo](https://drive.google.com/file/d/1cJzaQUNahjcg7BDnBrRkcf41yieNA4_e/view?usp=sharing)
🖼️ Screenshots:

![Screenshot 1]([link-to-image](https://drive.google.com/file/d/1VYitGC5BT_L6gEKYQWIva2rFZDAa8Acp/view?usp=sharing))

## 💡 Inspiration
Commercial bank lending service teams handle a significant number of servicing requests through emails. These emails contain diverse requests, often with attachments, that must be processed efficiently. Manually classifying and extracting key information from these emails is time-consuming and prone to errors.

This project was inspired by the need for **automated email classification**, ensuring accurate categorization and faster processing of service requests by redirecting to respective team.


## ⚙️ What It Does

This system automates the classification process by assigning **request types and sub-request types** to emails. The extracted information is structured in **JSON format**, making it easily processable by downstream systems. The system also extracts key details such as **confidence score, summary, priority, customer details, and attachment metadata** to improve automation and accuracy.


**Extracted Fields**

The system extracts the following key fields from emails:

- **`request_type`** – High-level category of the email request.
- **`sub_request_type`** – Specific request within the request type.
- **`confidence_score`** – The model’s confidence level in classification.
- **`summary`** – A brief summary of the email content.
- **`priority`** – Urgency level of the request.
- **`customer_name`** – Name of the customer associated with the request.
- **`account_number`** – Extracted bank account number (if available).
- **`loan_id`** – Loan identifier related to the email request.
- **`date`** – Date mentioned in the email (e.g., due date, request date).
- **`attachment_details`** – Information about attached documents (e.g., file type, extracted text if OCR is used).
- **`additional_data`** – Any other relevant extracted details to support processing.

## 🛠️ How We Built It
Briefly outline the technologies, frameworks, and tools used in development.

## 🚧 Challenges We Faced
- **Data Variability & Noise**: Loan-related emails contained a mix of structured, semi-structured, and unstructured text, making it difficult to extract relevant details consistently.
- **OCR Limitations**: Processing handwritten documents required robust OCR models, but accuracy varied based on document quality.
- **Model Training & Fine-Tuning**: LLMs needed extensive fine-tuning to correctly classify complex financial terminology and distinguish between similar loan-related requests.

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaied-prompt-pirates.git
   ```
2. Install dependencies 
- macOS 
   ```sh
   npm run setup 
   ```
- windows
   ```sh
   npm run win:setup 
   ```
3. Run the project  
   ```sh
   npm run app
   ```

## 🏗️ Tech Stack
- 🔹 Frontend: Next JS
- 🔹 Backend: FastAPI 
- 🔹 Other: Gemini API / OCR.Space Api  

## 👥 TEAM - PROMPT PIRATES
- **Vasu Gambhir** 
- **Neeraj Thazhekuniyil** 
- **Pranav Somaiah** 
- **Sibashis Khadanga** 
