file_test_data = [
    (
        "test.docx",
        """
            Context

            Scenario:
            Travelers planning international trips often need to compare accommodation prices in their local currency to better understand overall costs. Currently, the search functionality in the travel booking system allows filtering only by destination, travel dates, and the number of passengers. However, it does not provide an option to view prices in different currencies. This limitation can lead to confusion and make budgeting difficult, as travelers must manually convert prices using external tools.

            Challenges:
            •	Inability to filter prices by currency:
            Users cannot view accommodation prices in their preferred or local currency. This gap results in confusion and increases the potential for errors in cost estimation.
            •	Manual Currency Conversions:
            Without built-in currency conversion, users must rely on external tools or websites. These extra steps waste time and increase the risk of conversion mistakes.

            Requirements for User Story Generation:
            Add an advanced filtering option that allows users to view and compare accommodation prices in the following currencies:
            •	US Dollar
            •	Euro
            •	Japanese Yen
            •	British Pound Sterling
            •	Swiss Franc
            •	Canadian Dollar
            •	Australian Dollar
            •	Chinese Yuan Renminbi
            The system should display costs in the chosen currency, along with the currency code and numeric identifier, to help travelers more accurately budget and decide on accommodations. For example, AUD 36 Australian dollar.
        """,
    ),
    (
        "test.xlsx",
        """
            Column 1	Column 2	Column 3
            Cars	Test	222
            Data	Cats	111
            None	None	Travellers
        """,
    ),
    (
        "test.vtt",
        """
            WEBVTT

            00:00:00.500 --> 00:00:02.000
            The Web is always changing

            00:00:02.500 --> 00:00:04.300
            and the way we access it is changing
        """,
    ),
    (
        "test.ini",
        """
            [pytest]
            addopts = --slowmo 150
            # --browser-channel chrome --headed
            pythonpath = codemie-python
            filterwarnings =
                ignore::pytest.PytestUnknownMarkWarning
                ignore::urllib3.exceptions.InsecureRequestWarning

            rp_project = epm-cdme
            rp_launch = Pytest Regression
        """,
    ),
    (
        "test.csv",
        """
            The content of the file is:

            1918: 1922, track A: track B

            1918: 1944, track A: track C

            1918: 1991, track A: track D
        """,
    ),
    (
        "test.json",
        "The content in the context is from a source document titled 'Automation Test' and contains the word 'Test'.json",
    ),
    (
        "test.yaml",
        """
            The content in the context is a YAML configuration for an automated test scenario involving a file upload request.
            Here's the content detailed:
            file_upload_request:
              method: POST
              url: "https://example.com/upload"
              headers:
                accept: "application/json"
                Content-Type: "multipart/form-data"
              query_parameters:
                name: "example_file"
                description: "Sample file upload"
              form_data:
                files:
                  file_path: "path/to/sample.txt"
                  mime_type: "text/plain"
              expected_response:
                status_code: 200
                body: "Success"
             It includes details such as request headers, query parameters to include the name and description of the file,
              and form data specifying the file's path and MIME type. The expected response for a successful upload is a status code of `200`
               with a response body containing the word "Success".
        """,
    ),
    (
        "test.xml",
        """
            The content in the context is from a source document named `test.xml`. Here is the content of that document:
            <?xml version="1.0" encoding="UTF-8"?>
            <request>
                <method>POST</method>
                <url>https://example.com/api</url>
                <headers>
                    <header name="accept">application/json</header>
                    <header name="Content-Type">application/xml</header>
                </headers>
                <body>
                    <message>Hello, this is a test request.</message>
                </body>
            </request>
        """,
    ),
    (
        "test.pptx",
        """
            The content in the context, sourced from a document titled "test.pptx," covers an overview of software testing. Here's a summary of the key points:

            ### Introduction to Testing Concepts

            #### What is Software Testing?
            Software testing is defined as the process of evaluating and verifying that a software application operates as expected.

            #### Types of Software Testing
            - **Unit Testing**
            - **Integration Testing**
            - **System Testing**
            - **Acceptance Testing**

            #### Example Test Case
            - **Test Case:** Verify Login Functionality
                - **Steps:**
                    1. Open the login page.
                    2. Enter valid credentials.
                    3. Click login.
                    4. Verify successful login.

            #### Conclusion
            The document concludes by emphasizing that software testing is crucial for ensuring applications work as intended, thereby reducing bugs and enhancing quality.pptx
        """,
    ),
    (
        "test.pdf",
        """
            It contains a simple message stating "This file is for test purpose."
            followed by some whitespace and a separator line.
        """,
    ),
    (
        "test.txt",
        """
            The KB contains the following information:
                   
            **Source:** test.txt  
            **File Content:** This file is for test purpose.
        """,
    ),
    (
        "test.gif",
        """
            The image is a GIF showing a dog that appears to be smiling or showing its teeth in a playful manner.
            The dog is sitting on a couch, and its expression conveys a sense of humor or cuteness in its
            interaction with the person or object off-camera. The environment around the dog suggests it is
            in a living room setting, possibly with a television or other furnishings in the background.
            The dog's expression may appear as if it's imitating a human smile,
            which often results in comical interpretations in GIFs and memes.
        """,
    ),
    (
        "test.jpeg",
        """
            The image shows a Labrador Retriever dog sitting on a tile floor in what appears to be a kitchen.
            The dog is light-colored with a happy expression and an open mouth, possibly panting.
            It is wearing a collar with a name tag. In the background, you can see parts of the kitchen,
            including cabinets, a towel hanging from a cabinet handle, and various items on the countertop.
            The lighting gives a warm tone to the image,
            possibly indicating natural light coming in from a nearby window.
        """,
    ),
    (
        "test.jpg",
        """
            The image shows a Labrador Retriever dog sitting on a tile floor in what appears to be a kitchen.
            The dog is light-colored with a happy expression and an open mouth, possibly panting.
            It is wearing a collar with a name tag. In the background, you can see parts of the kitchen,
            including cabinets, a towel hanging from a cabinet handle, and various items on the countertop.
            The lighting gives a warm tone to the image,
            possibly indicating natural light coming in from a nearby window.
        """,
    ),
    (
        "test.png",
        """
            The image shows a Labrador Retriever dog sitting on a tile floor in what appears to be a kitchen.
            The dog is light-colored with a happy expression and an open mouth, possibly panting.
            It is wearing a collar with a name tag. In the background, you can see parts of the kitchen,
            including cabinets, a towel hanging from a cabinet handle, and various items on the countertop.
            The lighting gives a warm tone to the image,
            possibly indicating natural light coming in from a nearby window.
        """,
    ),
]


large_files_test_data = [
    "large_file.txt",
]

files_with_different_types_test_data = [
    "test.txt",
    "test.vtt",
    "test.csv",
    "test.json",
    "test.yaml",
    "test.xml",
    "test.pdf",
    "test.pptx",
    "test.gif",
    "test.jpeg",
    "test.jpg",
    "test.png",
    "test.docx",
    "test.xlsx",
    "test.ini",
]


RESPONSE_FOR_TWO_FILES_INDEXED = """
    We have the following types of data available:

    1. **CSV Data:**
       - Example data from a CSV file:
         ```
         1918: 1922
         track A: track B
    
         1918: 1944
         track A: track C
    
         1918: 1991
         track A: track D
     ```

    2. **Automation Test Data:**
       - Example data from an automation test labeled as:
         ```
         Test
         ```
"""

RESPONSE_FOR_TWO_FILES_UPLOADED = """
    Here is the content of the files:
    
    <test.docx>
    # Context
    
    **Scenario:**
    
    Travelers planning international trips often need to compare accommodation prices in their local currency to better understand overall costs. Currently, the search functionality in the travel booking system allows filtering only by destination, travel dates, and the number of passengers. However, it does not provide an option to view prices in different currencies. This limitation can lead to confusion and make budgeting difficult, as travelers must manually convert prices using external tools.
    
    **Challenges:**
    
    * Inability to filter prices by currency:
    
    Users cannot view accommodation prices in their preferred or local currency. This gap results in confusion and increases the potential for errors in cost estimation.
    
    * Manual Currency Conversions:
    
    Without built-in currency conversion, users must rely on external tools or websites. These extra steps waste time and increase the risk of conversion mistakes.
    
    **Requirements for User Story Generation:**
    
    Add an advanced filtering option that allows users to view and compare accommodation prices in the following currencies:
    
    * US Dollar
    * Euro
    * Japanese Yen
    * British Pound Sterling
    * Swiss Franc
    * Canadian Dollar
    * Australian Dollar
    * Chinese Yuan Renminbi
    
    The system should display costs in the chosen currency, along with the currency code and numeric identifier, to help travelers more accurately budget and decide on accommodations. For example, ***AUD 36 Australian dollar***.
    
    <test.ini>
    [pytest]
    addopts = --slowmo 150
    # --browser-channel chrome --headed
    pythonpath = codemie-python
    filterwarnings =
        ignore::pytest.PytestUnknownMarkWarning
        ignore::urllib3.exceptions.InsecureRequestWarning
    
    rp_project = epm-cdme
    rp_launch = Pytest Regression
"""
