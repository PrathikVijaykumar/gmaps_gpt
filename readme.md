# G Maps GPT

**G Maps GPT** is an intelligent assistant for querying and analyzing condominium data in Miami. It leverages natural language processing (NLP) to interpret user queries and provide actionable insights about condo buildings, units, sales, and market trends. The system is tailored to empower real estate agents and investors by making high-level data analysis accessible without technical expertise.

---

## **Supported Markets**
- **South Beach**
- **Miami Beach**
- **South of Fifth**

---

## **Purpose**
To enable real estate agents and investors to:
- Effortlessly perform high-level analyses.
- Make informed investment decisions quickly and accurately.
- Visualize data insights through interactive charts, maps, and PDF reports.

---

## **Features**
- **Natural Language Interface**: Query condo data effortlessly using plain English.
- **Google Maps API Integration**: Perform location-based queries with ease.
- **Dynamic SQL Generation**: Supports complex database queries without manual SQL writing.
- **Interactive Visualizations**: Data-driven charts and maps for easy interpretation.
- **PDF Report Generation**: Export detailed analyses for offline use.
- **Spelling Corrections & Address Resolution**: Employs vector embeddings and fuzzy logic for correcting user input and finding relevant addresses.
- **Serverless PostgreSQL**: Dynamically scales based on traffic demand.
- **GitHub Integration**: Fully integrated with version control for streamlined updates and maintenance.

---

## **Technologies Used**
- **Python 3.x**
- **Flask**: Web application framework.
- **Neon Tech**: Serverless PostgreSQL database.
- **LangChain & LangGraph**: Intelligent agents for NLP.
- **OpenAI GPT Models**: Natural language understanding.
- **Google Maps API**: Geocoding and directions.
- **Chart.js**: Data visualization.
- **ReportLab**: PDF generation.
- **Render**: Deployment platform.

---

## **Usage**
1. Enter natural language questions about Miami condos in the input field.
2. The system processes your query, retrieves relevant data, and displays insights.
3. For location-based queries, interactive maps are generated using Google Maps.
4. Data insights are visualized through dynamic charts and graphs.
5. Generate detailed PDF reports for offline review.
6. Use the "Clear Memory" button to reset conversation history.

---

## **Project Structure**
- `server.py`: Flask application server.
- `main.py`: Core logic for processing user queries and generating responses.
- `tools.py`: Custom tools for database querying and API interactions.
- `prefix.py`: AI system message prefix for guiding query interpretation.
- `boilerplate.py`: Code for map and chart generation.

---

## **Additional Features**
1. **Vector Embeddings & Fuzzy Logic**: Custom-built vector database (FAISS) and `difflib` for intelligent spelling corrections and address resolution.
2. **Serverless PostgreSQL**: Automatically scales to handle traffic spikes, ensuring seamless performance.
3. **GitHub Integration**: Enables efficient version control and deployment workflows.

---

## **Live Application**
Access the application here: [G Maps GPT](https://gmaps-gpt.onrender.com)

---

## **Future Enhancements**
- Expanding supported markets beyond Miami.
- Enhanced visualization tools for deeper data analysis.
- Real-time property trend updates.

For any questions or contributions, feel free to open an issue or create a pull request in the repository.
