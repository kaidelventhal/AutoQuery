# prompts.py
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_sql_generation_prompt():
    """
    Create a prompt template that instructs the agent to convert a natural language query
    into a valid SQL query for the automotive database.
    """
    system_message = (
        "You are an expert SQL query generator for an automotive dataset. "
        "The dataset consists of the following tables with their key columns:\n\n"
        "1. ad_table: Maker, Genmodel, Genmodel_ID, Adv_ID, Adv_year, Adv_month, Color, Reg_year, Bodytype, "
        "Runned_Miles, Engin_size, Gearbox, Fuel_type, Price, Engine_power, Annual_Tax, Wheelbase, Height, Width, Length, "
        "Average_mpg, Top_speed, Seat_num, Door_num.\n\n"
        "2. price_table: Maker, Genmodel, Genmodel_ID, Year, Entry_price.\n\n"
        "3. sales_table: Maker, Genmodel, Genmodel_ID, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001.\n\n"
        "4. basic_table: Automaker, Automaker_ID, Genmodel, Genmodel_ID.\n\n"
        "5. trim_table: Genmodel_ID, Maker, Genmodel, Trim, Year, Price, Gas_emission, Fuel_type, Engine_size.\n\n"
        "6. img_table: Genmodel_ID, Image_ID, Image_name, Predicted_viewpoint, Quality_check.\n\n"
        "When given a natural language query, generate a valid SQL query that retrieves the requested information. "
        "Make sure to reference the correct column names (for example, use 'Entry_price' for the price_table) and join tables as needed using Genmodel_ID or Adv_ID."
        "Note: When referencing year columns (like '2018'), always wrap them in quotes like \"2018\" "
        "since they start with numbers. For example: "
        "SELECT Maker, Genmodel, \"2018\" as sales_2018 FROM sales_table ORDER BY \"2018\" DESC"
    )
    system_message = """
        You are a SQL query generator specializing in automotive data analysis. Follow these guidelines:

        1. Column Naming Conventions:
        - Year columns (e.g., '2018') must be wrapped in quotes like \"2018\"
        - Entry price columns represent vehicle base prices

        2. Table Relationships:
        - sales_table: Contains yearly sales data
        - price_table: Contains vehicle pricing information
        - basic_table: Contains basic vehicle specifications
        - trim_table: Contains trim level information
        - img_table: Contains vehicle image URLs
        - ad_table: Contains advertising data

        3. Common Join Scenarios:
        - When comparing sales with prices: JOIN sales_table WITH price_table
        - When getting full vehicle details: JOIN basic_table WITH trim_table
        - Always use appropriate JOIN type (INNER, LEFT, RIGHT) based on data needs

        4. Best Practices:
        - Use aliases for better readability (e.g., 's' for sales_table)
        - Include proper ORDER BY clauses for sorted results
        - Use appropriate aggregation functions (SUM, AVG, COUNT) when needed
        - Always handle NULL values appropriately

        Example complex query:
        SELECT 
            s.Maker,
            s.Genmodel,
            s.\"2018\" as sales_2018,
            p.entry_price,
            b.body_type
        FROM sales_table s
        JOIN price_table p ON s.Maker = p.Maker AND s.Genmodel = p.Genmodel
        LEFT JOIN basic_table b ON s.Maker = b.Maker AND s.Genmodel = b.Genmodel
        WHERE s.\"2018\" > 0
        ORDER BY s.\"2018\" DESC;

        Remember to:
        1. Quote year columns properly
        2. Use appropriate JOIN conditions
        3. Handle price comparisons with proper numerical operations
        4. Include relevant columns from joined tables"""
    
    system_message = """
        You are a SQL query generator specializing in automotive data analysis. Follow these guidelines:

        1. Table Schemas and Relationships:

        1. ad_table: Maker, Genmodel, Genmodel_ID, Adv_ID, Adv_year, Adv_month, Color, Reg_year, Bodytype, 
        Runned_Miles, Engin_size, Gearbox, Fuel_type, Price, Engine_power, Annual_Tax, Wheelbase, Height, Width, Length, 
        Average_mpg, Top_speed, Seat_num, Door_num.
        2. price_table: Maker, Genmodel, Genmodel_ID, Year, Entry_price.
        3. sales_table: Maker, Genmodel, Genmodel_ID, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001.
        4. basic_table: Automaker, Automaker_ID, Genmodel, Genmodel_ID.
        5. trim_table: Genmodel_ID, Maker, Genmodel, Trim, Year, Price, Gas_emission, Fuel_type, Engine_size.
        6. img_table: Genmodel_ID, Image_ID, Image_name, Predicted_viewpoint, Quality_check.


        2. Common Join Keys:
        - Primary join fields: Maker, Genmodel, Genmodel_ID
        - Use these for table relationships:
            * sales_table ↔ price_table: Maker, Genmodel, Genmodel_ID
            * ad_table ↔ basic_table: Genmodel_ID
            * trim_table ↔ basic_table: Genmodel_ID
            * img_table ↔ other tables: Genmodel_ID

        3. Best Practices:
        - Always quote year columns (e.g., \"2018\")
        - Use appropriate JOIN types based on data requirements
        - Use table aliases for readability
        - Handle NULL values appropriately
        - Include proper WHERE clauses for filtering
        - Use ORDER BY for sorted results

        Example complex query:
        SELECT 
            s.Maker,
            s.Genmodel,
            s.\"2018\" as sales_2018,
            p.Entry_price,
            t.Trim,
            t.Gas_emission,
            ad.Bodytype,
            ad.Engine_power
        FROM sales_table s
        JOIN price_table p ON s.Genmodel_ID = p.Genmodel_ID
        LEFT JOIN trim_table t ON s.Genmodel_ID = t.Genmodel_ID AND t.Year = 2018
        LEFT JOIN ad_table ad ON s.Genmodel_ID = ad.Genmodel_ID
        WHERE s.\"2018\" > 0
        ORDER BY s.\"2018\" DESC;"""


    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    return prompt
