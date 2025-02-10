# AutoQuery AI

## Project Description

AutoQuery AI is an intelligent vehicle recommendation and query assistant designed to help users find the perfect vehicle based on their preferences. Leveraging advanced natural language processing and large language models, AutoQuery AI allows users to interact with a chat-based interface to query a comprehensive vehicle sales dataset. The project utilizes Google Vertex AI, LangChain, and LangGraph to provide optimized and accurate query results.

## Features

- **Natural Language Interface**: Users can ask questions in plain English to find vehicles that match their criteria.
- **Agentic AI Query Processing**: Converts natural language queries into optimized SQL queries using LLMs.
- **Data-Driven Recommendations**: Provides personalized vehicle recommendations based on user queries and historical data.

## Tech Stack

- **Google Vertex AI**: For hosting and managing LLM models.
- **LangChain & LangGraph**: For orchestrating prompt chains and optimizing queries.
- **Python**: For data processing and backend development.
- **PandasSQL**: For querying the dataset efficiently.
- **Flask/Streamlit**: For building the chat interface.

## Getting Started

### Prerequisites

- Python 3.8+
- Pandas
- PandasSQL
- Flask/Streamlit

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/autoquery-ai.git
    cd autoquery-ai
    ```

2. Install the required packages:
    ```bash
    pip install pandas pandasql flask streamlit
    ```

### Usage

1. Load the datasets:
    ```python
    import os
    import pandas as pd
    import pandasql as ps

    # Define your table directory
    TABLE_DIR = 'path/to/your/csv/files'

    # Load the CSV tables into pandas DataFrames
    ad_table = pd.read_csv(os.path.join(TABLE_DIR, 'Ad_table.csv'))
    price_table = pd.read_csv(os.path.join(TABLE_DIR, 'Price_table.csv'))
    sales_table = pd.read_csv(os.path.join(TABLE_DIR, 'Sales_table.csv'))
    basic_table = pd.read_csv(os.path.join(TABLE_DIR, 'Basic_table.csv'))
    trim_table = pd.read_csv(os.path.join(TABLE_DIR, 'Trim_table.csv'))
    img_table = pd.read_csv(os.path.join(TABLE_DIR, 'Image_table.csv'))
    ```

2. Run a sample query using PandasSQL:
    ```python
    query = """
    SELECT ad_table.Maker, ad_table.Genmodel, ad_table.Reg_year, ad_table.Bodytype, ad_table.Color, ad_table.Price, price_table.Entry_price, sales_table.2018
    FROM ad_table
    JOIN price_table ON ad_table.Genmodel_ID = price_table.Genmodel_ID
    JOIN sales_table ON ad_table.Genmodel_ID = sales_table.Genmodel_ID
    WHERE ad_table.Reg_year >= 2018 AND ad_table.Bodytype = 'Sedan' AND ad_table.Color = 'Red'
    """
    result_df = ps.sqldf(query, locals())
    print(result_df)
    ```

3. Develop the chat interface and integrate with LangChain for natural language to SQL conversion.

## Future Enhancements

- Integrate vehicle images for enriched recommendations.
- Provide trend analytics and pricing predictions.
- Expand the assistant to handle more complex queries and provide deeper insights.

## Conclusion

AutoQuery AI showcases advanced AI techniques and data science skills, making it a valuable addition to your portfolio. It demonstrates your ability to build intelligent, data-driven applications that solve real-world problems.
