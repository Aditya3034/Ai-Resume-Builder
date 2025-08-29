import os
import asyncio
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langgraph.graph import MessagesState

# Import your existing functions
from app.utils.helpers import (
    extract_github_data,
    scrape_portfolio,
    extract_jd_keywords,
    pdf_to_text,
    generate_resume_json
)

# ===============================
# WORKER AGENTS (Specialized Agents)
# ===============================

def create_github_agent():
    """GitHub agent - extracts GitHub repository data"""
    
    @tool
    def fetch_github_data(github_url: str) -> str:
        """Extract comprehensive GitHub repository data from the provided URL"""
        try:
            print(f"🔍 Fetching GitHub data from: {github_url}")
            data = extract_github_data(github_url)
            result = f"GitHub data successfully extracted for {data['username']}: {data['total_public_repos']} repos, {data['total_user_commits']} commits, most recent repo: {data['most_recent_repo']}"
            print(f"✅ GitHub data fetched successfully")
            return result
        except Exception as e:
            error_msg = f"❌ Error extracting GitHub data: {str(e)}"
            print(error_msg)
            return error_msg
    
    return create_react_agent(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        tools=[fetch_github_data],
        prompt="""You are the GitHub Agent specializing in extracting GitHub repository data.

INSTRUCTIONS:
- When given a GitHub URL, use the fetch_github_data tool to extract comprehensive repository information
- Extract user statistics, project details, commit history, and repository metadata  
- After completing your task, respond to the supervisor with the extracted data
- Respond ONLY with the results of your work, do NOT include any other text.""",
        name="github_agent"
    )

def create_portfolio_agent():
    """Portfolio agent - scrapes portfolio websites"""
    
    @tool
    def scrape_portfolio_data(portfolio_url: str) -> str:
        """Scrape comprehensive content from portfolio website"""
        try:
            print(f"🌐 Scraping portfolio from: {portfolio_url}")
            doc = scrape_portfolio(portfolio_url)
            result = f"Portfolio content successfully scraped. Content length: {len(doc.page_content)} characters. Content preview: {doc.page_content[:200]}..."
            print(f"✅ Portfolio scraping completed")
            return result
        except Exception as e:
            error_msg = f"❌ Error scraping portfolio: {str(e)}"
            print(error_msg)
            return error_msg
    
    return create_react_agent(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        tools=[scrape_portfolio_data],
        prompt="""You are the Portfolio Agent specializing in scraping portfolio websites.

INSTRUCTIONS:  
- When given a portfolio URL, use the scrape_portfolio_data tool to extract all relevant content
- Extract personal information, skills, projects, experience, and any other professional details
- After completing your task, respond to the supervisor with the scraped content
- Respond ONLY with the results of your work, do NOT include any other text.""",
        name="portfolio_agent"
    )

def create_jd_keywords_agent():
    """JD Keywords agent - extracts keywords from job descriptions"""
    
    @tool 
    def extract_keywords_from_jd(job_description: str) -> str:
        """Extract ATS-friendly keywords from job description for resume optimization"""
        try:
            print(f"🎯 Extracting keywords from job description...")
            keywords = extract_jd_keywords(job_description)
            result = f"Keywords successfully extracted ({len(keywords)} keywords): {', '.join(keywords)}"
            print(f"✅ Keywords extraction completed: {len(keywords)} keywords found")
            return result
        except Exception as e:
            error_msg = f"❌ Error extracting keywords: {str(e)}"
            print(error_msg)
            return error_msg
    
    return create_react_agent(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        tools=[extract_keywords_from_jd],
        prompt="""You are the JD Keywords Agent specializing in extracting ATS-friendly keywords.

INSTRUCTIONS:
- When given a job description, use the extract_keywords_from_jd tool to identify relevant keywords
- Extract technical skills, action verbs, industry terms, and ATS-optimization keywords
- After completing your task, respond to the supervisor with the extracted keywords
- Respond ONLY with the results of your work, do NOT include any other text.""",
        name="jd_keywords_agent"
    )

def create_content_writer_agent():
    """Content Writer agent - generates the final resume JSON"""
    
    @tool
    def generate_comprehensive_resume(
        github_data: str = "",
        portfolio_data: str = "", 
        jd_keywords: str = "",
        old_resume_text: str = "",
        user_additions: str = "",
        user_feedback: str = ""
    ) -> str:
        """Generate comprehensive resume JSON using all collected data from previous agents"""
        try:
            print(f"📝 Generating comprehensive resume with collected data...")
            
            # Parse keywords back to list format
            keywords_list = [kw.strip() for kw in jd_keywords.split(',')] if jd_keywords else []
            
            # Call your actual resume generation function
            resume = generate_resume_json(
                github_data=github_data,
                portfolio_data=portfolio_data,
                jd_keywords=keywords_list,
                old_resume=old_resume_text,
                user_additions=user_additions,
                user_feedback=user_feedback
            )
            
            result = f"✅ Resume successfully generated with structured JSON format including: personal info, summary, skills, experience, education, projects, and optimized keywords"
            print(f"✅ Resume generation completed successfully")
            return result
        except Exception as e:
            error_msg = f"❌ Error generating resume: {str(e)}"
            print(error_msg)
            return error_msg
    
    return create_react_agent(
        model=init_chat_model("openai:gpt-4"),  # Use GPT-4 for the final generation
        tools=[generate_comprehensive_resume],
        prompt="""You are the Content Writer Agent specializing in generating comprehensive, ATS-friendly resumes.

INSTRUCTIONS:
- Use the generate_comprehensive_resume tool with all data collected by previous agents
- Incorporate GitHub projects, portfolio content, job description keywords, and old resume information
- Generate a structured JSON resume optimized for ATS systems with proper keyword integration
- After completing your task, respond to the supervisor with the final resume confirmation
- Respond ONLY with the results of your work, do NOT include any other text.""",
        name="content_writer_agent"
    )

# ===============================
# SUPERVISOR WORKFLOW CREATION
# ===============================

def create_resume_generation_supervisor():
    """Create the resume generation supervisor using langgraph-supervisor"""
    
    # Create specialized worker agents (removed PDF converter)
    github_agent = create_github_agent()
    portfolio_agent = create_portfolio_agent()
    jd_keywords_agent = create_jd_keywords_agent()
    content_writer_agent = create_content_writer_agent()
    
    # Create supervisor using langgraph-supervisor
    supervisor = create_supervisor(
        model=init_chat_model("openai:gpt-4"),
        agents=[
            github_agent,
            portfolio_agent, 
            jd_keywords_agent,
            content_writer_agent
        ],
        prompt=(
            "You are a Resume Generation Supervisor managing specialized agents:\n"
            "- github_agent: Extract GitHub repository data when GitHub URL is provided\n"
            "- portfolio_agent: Scrape portfolio website content when portfolio URL is provided\n"
            "- jd_keywords_agent: Extract keywords from job descriptions when JD is provided\n"  
            "- content_writer_agent: Generate final resume JSON using ALL collected data\n\n"
            "WORKFLOW RULES:\n"
            "1. First, assign data collection tasks to appropriate agents based on available inputs\n"
            "2. Process GitHub, portfolio, and JD keywords tasks in any order (they're independent)\n"
            "3. ONLY call content_writer_agent LAST, after ALL other data collection is complete\n"
            "4. Assign work to one agent at a time, do not call agents in parallel\n"
            "5. Do not do any work yourself - only coordinate and delegate\n"
            "6. Old resume text will be provided directly to content_writer_agent, no conversion needed"
        ),
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile()
    
    return supervisor

# ===============================
# MAIN EXECUTION FUNCTION
# ===============================

async def generate_resume_workflow(
    github_url: Optional[str] = None,
    portfolio_url: Optional[str] = None, 
    job_description: Optional[str] = None,
    old_resume_text: Optional[str] = None,  # Changed from old_resume_pdf to old_resume_text
    user_feedback: Optional[str] = None,
    user_additions: Optional[str] = None
):
    """Execute the complete resume generation workflow using supervisor pattern"""
    
    # Build input summary for logging
    inputs_provided = []
    if github_url: inputs_provided.append("GitHub URL")
    if portfolio_url: inputs_provided.append("Portfolio URL")
    if job_description: inputs_provided.append("Job Description")
    if old_resume_text: inputs_provided.append("Old Resume Text")  # Updated
    if user_feedback: inputs_provided.append("User Feedback")  
    if user_additions: inputs_provided.append("User Additions")
    
    # Create the user request message
    user_request = f"""Please generate a comprehensive resume using these inputs:

📋 AVAILABLE INPUTS:
{', '.join(inputs_provided) if inputs_provided else 'None provided'}

📝 DETAILS:
- GitHub URL: {github_url or 'Not provided'}
- Portfolio URL: {portfolio_url or 'Not provided'}
- Job Description: {'Provided ✓' if job_description else 'Not provided ✗'}
- Old Resume Text: {'Provided ✓' if old_resume_text else 'Not provided ✗'}  
- User Feedback: {user_feedback or 'Not provided'}
- User Additions: {user_additions or 'Not provided'}

🎯 TASK: Please coordinate the workflow to:
1. Process all available inputs using appropriate specialized agents
2. Generate a final comprehensive resume using all collected data
3. The old resume text (if provided) should be passed directly to the content writer agent

📄 OLD RESUME CONTENT:
{old_resume_text if old_resume_text else 'No old resume provided'}
"""
    
    # Create supervisor and run workflow
    supervisor = create_resume_generation_supervisor()
    
    print("🚀 Starting Resume Generation Supervisor Workflow")
    print(f"📊 Processing: {', '.join(inputs_provided) if inputs_provided else 'No inputs'}")
    print("=" * 60)
    
    # Execute the workflow
    result = supervisor.invoke({
        "messages": [{"role": "user", "content": user_request}]
    })
    
    print("=" * 60)
    print("✅ Resume Generation Workflow Completed!")
    
    return result

# ===============================
# EXAMPLE USAGE
# ===============================

if __name__ == "__main__":
    async def main():
        # Example with multiple inputs including old resume text
        old_resume_sample = """
        John Doe
        Software Engineer
        Email: john@example.com
        
        EXPERIENCE:
        - Senior Developer at TechCorp (2020-2024)
        - Built scalable web applications using Python and React
        - Led team of 5 developers on major projects
        
        SKILLS:
        Python, JavaScript, React, AWS, Docker
        """
        
        result = await generate_resume_workflow(
            github_url="https://github.com/yourusername",
            portfolio_url="https://yourportfolio.com",
            job_description="""Senior Software Engineer position requiring:
            - 5+ years Python/JavaScript experience
            - React, Node.js, AWS cloud platforms
            - Machine learning and data analysis skills
            - Leadership and team collaboration
            - Agile development methodologies""",
            old_resume_text=old_resume_sample,  # Pass text directly
            user_feedback="Highlight my machine learning projects and open source contributions",
            user_additions="Add AWS Solutions Architect certification earned in 2024"
        )
        
        print("\n🎉 Final Result:")
        print(result["messages"][-1].content)
    
    # Run the workflow
    asyncio.run(main())

# For testing individual components
def test_individual_agents():
    """Test individual agents independently"""
    
    # Test GitHub agent
    github_agent = create_github_agent()
    github_result = github_agent.invoke({
        "messages": [{"role": "user", "content": "Extract data from https://github.com/octocat"}]
    })
    print("GitHub Agent Result:", github_result["messages"][-1].content)
    
    # Test Portfolio agent  
    portfolio_agent = create_portfolio_agent()
    portfolio_result = portfolio_agent.invoke({
        "messages": [{"role": "user", "content": "Scrape https://example-portfolio.com"}]
    })
    print("Portfolio Agent Result:", portfolio_result["messages"][-1].content)
    
    # Test JD Keywords agent
    jd_agent = create_jd_keywords_agent()
    jd_result = jd_agent.invoke({
        "messages": [{"role": "user", "content": "Extract keywords from: Senior Python Developer position requiring Flask, Django, AWS"}]
    })
    print("JD Keywords Agent Result:", jd_result["messages"][-1].content)

if __name__ == "__main__":
    # Uncomment to test individual agents
    # test_individual_agents()
    
    # Run main workflow
    asyncio.run(main())
