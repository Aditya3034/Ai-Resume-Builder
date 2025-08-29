import os
import asyncio
from typing import Dict, List, Optional, Any, Set
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
# GLOBAL CALL TRACKING SYSTEM
# ===============================
class CallTracker:
    """Thread-safe call tracker to prevent multiple agent executions"""
    
    def __init__(self):
        self.called_agents: Set[str] = set()
        self.completed_tasks: Dict[str, bool] = {}
        self.task_results: Dict[str, str] = {}
        self._lock = asyncio.Lock()
    
    async def is_agent_called(self, agent_name: str) -> bool:
        """Check if agent has already been called"""
        async with self._lock:
            return agent_name in self.called_agents
    
    async def mark_agent_called(self, agent_name: str) -> bool:
        """Mark agent as called, returns True if successful, False if already called"""
        async with self._lock:
            if agent_name in self.called_agents:
                return False
            self.called_agents.add(agent_name)
            return True
    
    async def mark_task_completed(self, task_name: str, result: str, success: bool = True):
        """Mark task as completed with result"""
        async with self._lock:
            self.completed_tasks[task_name] = success
            self.task_results[task_name] = result
    
    async def is_task_completed(self, task_name: str) -> bool:
        """Check if task is completed"""
        async with self._lock:
            return self.completed_tasks.get(task_name, False)
    
    async def get_task_result(self, task_name: str) -> str:
        """Get task result"""
        async with self._lock:
            return self.task_results.get(task_name, "")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current tracking status"""
        async with self._lock:
            return {
                "called_agents": list(self.called_agents),
                "completed_tasks": dict(self.completed_tasks),
                "task_results": dict(self.task_results)
            }
    
    async def reset(self):
        """Reset all tracking (use with caution)"""
        async with self._lock:
            self.called_agents.clear()
            self.completed_tasks.clear()
            self.task_results.clear()

# Global tracker instance
call_tracker = CallTracker()

# ===============================
# WORKER AGENTS WITH CALL PROTECTION
# ===============================
def create_github_agent():
    """GitHub agent with single-call protection"""
    
    @tool
    async def fetch_github_data(github_url: str) -> str:
        """Extract comprehensive GitHub repository data from the provided URL"""
        agent_name = "github_agent"
        
        # Check if already called
        if await call_tracker.is_agent_called(agent_name):
            existing_result = await call_tracker.get_task_result("github_task")
            return f"ALREADY_CALLED: GitHub agent was already executed. Previous result: {existing_result}"
        
        # Mark as called
        if not await call_tracker.mark_agent_called(agent_name):
            return "CALL_BLOCKED: GitHub agent call was blocked due to concurrent execution"
        
        try:
            print(f"🔍 [SINGLE CALL] Fetching GitHub data from: {github_url}")
            data = extract_github_data(github_url)
            result = f"SUCCESS: GitHub data extracted for {data['username']}: {data['total_public_repos']} repos, {data['total_user_commits']} commits, most recent repo: {data['most_recent_repo']}"
            print(f"✅ [SINGLE CALL] GitHub data fetched successfully")
            
            # Mark task as completed
            await call_tracker.mark_task_completed("github_task", result, True)
            return f"GITHUB_TASK_COMPLETED: {result}"
            
        except Exception as e:
            error_msg = f"ERROR: Failed to extract GitHub data from {github_url}: {str(e)}"
            print(f"❌ [SINGLE CALL] {error_msg}")
            
            # Mark task as failed
            await call_tracker.mark_task_completed("github_task", error_msg, False)
            return f"GITHUB_TASK_FAILED: {error_msg}"
    
    return create_react_agent(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        tools=[fetch_github_data],
        prompt="""You are the GitHub Agent with SINGLE-CALL PROTECTION specializing in extracting GitHub repository data.
CRITICAL RULES:
- You can only be called ONCE per workflow execution
- If you see "ALREADY_CALLED" in the response, DO NOT attempt the task again
- If you see "CALL_BLOCKED", acknowledge and report the blocking
- When given a GitHub URL, use the fetch_github_data tool ONCE to extract comprehensive repository information
- After completing your task successfully, respond with "GITHUB_TASK_COMPLETED" followed by the extracted data
- If you encounter an error, respond with "GITHUB_TASK_FAILED" followed by the error details
- NEVER retry failed requests - report the failure and stop""",
        name="github_agent"
    )

def create_portfolio_agent():
    """Portfolio agent with single-call protection"""
    
    @tool
    async def scrape_portfolio_data(portfolio_url: str) -> str:
        """Scrape comprehensive content from portfolio website"""
        agent_name = "portfolio_agent"
        
        # Check if already called
        if await call_tracker.is_agent_called(agent_name):
            existing_result = await call_tracker.get_task_result("portfolio_task")
            return f"ALREADY_CALLED: Portfolio agent was already executed. Previous result: {existing_result}"
        
        # Mark as called
        if not await call_tracker.mark_agent_called(agent_name):
            return "CALL_BLOCKED: Portfolio agent call was blocked due to concurrent execution"
        
        try:
            print(f"🌐 [SINGLE CALL] Scraping portfolio from: {portfolio_url}")
            doc = await scrape_portfolio(portfolio_url)
            result = f"SUCCESS: Portfolio content scraped from {portfolio_url}. Content length: {len(doc.page_content)} characters. Preview: {doc.page_content[:200]}..."
            print(f"✅ [SINGLE CALL] Portfolio scraping completed")
            
            # Mark task as completed
            await call_tracker.mark_task_completed("portfolio_task", result, True)
            return f"PORTFOLIO_TASK_COMPLETED: {result}"
            
        except Exception as e:
            error_msg = f"ERROR: Failed to scrape portfolio from {portfolio_url}: {str(e)}"
            print(f"❌ [SINGLE CALL] {error_msg}")
            
            # Mark task as failed
            await call_tracker.mark_task_completed("portfolio_task", error_msg, False)
            return f"PORTFOLIO_TASK_FAILED: {error_msg}"
    
    return create_react_agent(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        tools=[scrape_portfolio_data],
        prompt="""You are the Portfolio Agent with SINGLE-CALL PROTECTION specializing in scraping portfolio websites.
CRITICAL RULES:
- You can only be called ONCE per workflow execution
- If you see "ALREADY_CALLED" in the response, DO NOT attempt the task again
- If you see "CALL_BLOCKED", acknowledge and report the blocking
- When given a portfolio URL, use the scrape_portfolio_data tool ONCE to extract all relevant content
- Extract personal information, skills, projects, experience, and any other professional details
- After completing your task successfully, respond with "PORTFOLIO_TASK_COMPLETED" followed by the scraped content
- If you encounter an error, respond with "PORTFOLIO_TASK_FAILED" followed by the error details
- NEVER retry failed requests - report the failure and stop""",
        name="portfolio_agent"
    )

def create_jd_keywords_agent():
    """JD Keywords agent with single-call protection"""
    
    @tool
    async def extract_keywords_from_jd(job_description: str) -> str:
        """Extract ATS-friendly keywords from job description for resume optimization"""
        agent_name = "jd_keywords_agent"
        
        # Check if already called
        if await call_tracker.is_agent_called(agent_name):
            existing_result = await call_tracker.get_task_result("keywords_task")
            return f"ALREADY_CALLED: JD Keywords agent was already executed. Previous result: {existing_result}"
        
        # Mark as called
        if not await call_tracker.mark_agent_called(agent_name):
            return "CALL_BLOCKED: JD Keywords agent call was blocked due to concurrent execution"
        
        try:
            print(f"🎯 [SINGLE CALL] Extracting keywords from job description...")
            keywords = extract_jd_keywords(job_description)
            result = f"SUCCESS: Keywords extracted ({len(keywords)} keywords): {', '.join(keywords)}"
            print(f"✅ [SINGLE CALL] Keywords extraction completed: {len(keywords)} keywords found")
            
            # Mark task as completed
            await call_tracker.mark_task_completed("keywords_task", result, True)
            return f"KEYWORDS_TASK_COMPLETED: {result}"
            
        except Exception as e:
            error_msg = f"ERROR: Failed to extract keywords: {str(e)}"
            print(f"❌ [SINGLE CALL] {error_msg}")
            
            # Mark task as failed
            await call_tracker.mark_task_completed("keywords_task", error_msg, False)
            return f"KEYWORDS_TASK_FAILED: {error_msg}"
    
    return create_react_agent(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        tools=[extract_keywords_from_jd],
        prompt="""You are the JD Keywords Agent with SINGLE-CALL PROTECTION specializing in extracting ATS-friendly keywords.
CRITICAL RULES:
- You can only be called ONCE per workflow execution
- If you see "ALREADY_CALLED" in the response, DO NOT attempt the task again
- If you see "CALL_BLOCKED", acknowledge and report the blocking
- When given a job description, use the extract_keywords_from_jd tool ONCE to identify relevant keywords
- Extract technical skills, action verbs, industry terms, and ATS-optimization keywords
- After completing your task successfully, respond with "KEYWORDS_TASK_COMPLETED" followed by the extracted keywords
- If you encounter an error, respond with "KEYWORDS_TASK_FAILED" followed by the error details
- NEVER retry failed requests - report the failure and stop""",
        name="jd_keywords_agent"
    )

def create_content_writer_agent():
    """Content Writer agent with single-call protection"""
    
    @tool
    async def generate_comprehensive_resume(
        github_data: str = "",
        portfolio_data: str = "", 
        jd_keywords: str = "",
        old_resume_text: str = "",
        user_additions: str = "",
        user_feedback: str = ""
    ) -> str:
        """Generate comprehensive resume JSON using all collected data from previous agents"""
        agent_name = "content_writer_agent"
        
        # Check if already called
        if await call_tracker.is_agent_called(agent_name):
            existing_result = await call_tracker.get_task_result("resume_generation")
            return f"ALREADY_CALLED: Content Writer agent was already executed. Previous result: {existing_result}"
        
        # Mark as called
        if not await call_tracker.mark_agent_called(agent_name):
            return "CALL_BLOCKED: Content Writer agent call was blocked due to concurrent execution"
        
        try:
            print(f"📝 [SINGLE CALL] Generating comprehensive resume with collected data...")
            
            # Get actual results from previous agents
            github_result = await call_tracker.get_task_result("github_task")
            portfolio_result = await call_tracker.get_task_result("portfolio_task")
            keywords_result = await call_tracker.get_task_result("keywords_task")
            
            # Parse keywords back to list format
            keywords_list = []
            if keywords_result and "SUCCESS:" in keywords_result:
                keyword_part = keywords_result.split("SUCCESS:")[1].strip()
                if ":" in keyword_part:
                    keyword_part = keyword_part.split(":", 1)[1].strip()
                keywords_list = [kw.strip() for kw in keyword_part.split(',')] if keyword_part else []
            
            # Call your actual resume generation function
            resume_json = generate_resume_json(
                github_data=github_result,
                portfolio_data=portfolio_result,
                jd_keywords=keywords_list,
                old_resume=old_resume_text,
                user_additions=user_additions,
                user_feedback=user_feedback
            )
            
            # Store the actual resume JSON in a separate task result
            import json
            if isinstance(resume_json, dict):
                resume_json_str = json.dumps(resume_json)
            else:
                resume_json_str = str(resume_json)
            
            # Store the actual resume JSON
            await call_tracker.mark_task_completed("resume_json_data", resume_json_str, True)
            
            result = f"SUCCESS: Resume generated successfully"
            print(f"✅ [SINGLE CALL] Resume generation completed successfully")
            
            # Mark task as completed
            await call_tracker.mark_task_completed("resume_generation", result, True)
            return f"RESUME_GENERATION_COMPLETED: {result}"
            
        except Exception as e:
            error_msg = f"ERROR: Failed to generate resume: {str(e)}"
            print(f"❌ [SINGLE CALL] {error_msg}")
            
            # Mark task as failed
            await call_tracker.mark_task_completed("resume_generation", error_msg, False)
            return f"RESUME_GENERATION_FAILED: {error_msg}"

    
    return create_react_agent(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        tools=[generate_comprehensive_resume],
        prompt="""You are the Content Writer Agent with SINGLE-CALL PROTECTION specializing in generating comprehensive, ATS-friendly resumes.
CRITICAL RULES:
- You can only be called ONCE per workflow execution
- If you see "ALREADY_CALLED" in the response, DO NOT attempt the task again
- If you see "CALL_BLOCKED", acknowledge and report the blocking
- Use the generate_comprehensive_resume tool with all data collected by previous agents
- Incorporate GitHub projects, portfolio content, job description keywords, and old resume information
- Generate a structured JSON resume optimized for ATS systems with proper keyword integration
- After completing your task successfully, respond with "RESUME_GENERATION_COMPLETED" followed by confirmation details
- If you encounter an error, respond with "RESUME_GENERATION_FAILED" followed by the error details
- This is the FINAL step - only execute when ALL other agents have completed their tasks
- NEVER retry failed requests - report the failure and stop""",
        name="content_writer_agent"
    )

# ===============================
# ENHANCED SUPERVISOR WITH CALL TRACKING
# ===============================
def create_resume_generation_supervisor():
    """Create the resume generation supervisor with enhanced call tracking"""
    
    # Create specialized worker agents with call protection
    github_agent = create_github_agent()
    portfolio_agent = create_portfolio_agent()
    jd_keywords_agent = create_jd_keywords_agent()
    content_writer_agent = create_content_writer_agent()
    
    # Create supervisor with enhanced tracking
    supervisor = create_supervisor(
        model=init_chat_model("openai:gpt-3.5-turbo"),
        agents=[
            github_agent,
            portfolio_agent, 
            jd_keywords_agent,
            content_writer_agent
        ],
        prompt=(
            "You are a Resume Generation Supervisor with STRICT SINGLE-CALL ENFORCEMENT managing specialized agents:\n"
            "- github_agent: Extract GitHub repository data (CALL ONLY ONCE)\n"
            "- portfolio_agent: Scrape portfolio website content (CALL ONLY ONCE)\n"
            "- jd_keywords_agent: Extract keywords from job descriptions (CALL ONLY ONCE)\n"  
            "- content_writer_agent: Generate final resume JSON (CALL ONLY ONCE)\n\n"
            "CRITICAL SINGLE-CALL RULES:\n"
            "🚫 NEVER assign the same agent twice - each agent can only be called ONCE per workflow\n"
            "🚫 If you see 'ALREADY_CALLED' or 'CALL_BLOCKED', DO NOT retry that agent\n"
            "🚫 If an agent reports completion or failure, mark it as DONE and move on\n"
            "🚫 Do not get stuck in loops - track which agents have been called\n\n"
            "WORKFLOW RULES:\n"
            "1. Assign each task ONLY ONCE to the appropriate agent based on available inputs\n"
            "2. Track completed tasks by looking for completion messages (e.g., 'GITHUB_TASK_COMPLETED')\n"
            "3. Process data collection tasks (GitHub, portfolio, keywords) first in any order\n"
            "4. ONLY call content_writer_agent LAST, after data collection attempts are complete\n"
            "5. If an agent reports task completion, mark that task as DONE and move on\n"
            "6. If an agent reports task failure, note the failure but continue with other tasks\n"
            "7. Coordinate efficiently - prevent duplicate work and infinite loops\n\n"
            "TASK COMPLETION INDICATORS:\n"
            "- GitHub: Look for 'GITHUB_TASK_COMPLETED', 'GITHUB_TASK_FAILED', or 'ALREADY_CALLED'\n"
            "- Portfolio: Look for 'PORTFOLIO_TASK_COMPLETED', 'PORTFOLIO_TASK_FAILED', or 'ALREADY_CALLED'\n"
            "- Keywords: Look for 'KEYWORDS_TASK_COMPLETED', 'KEYWORDS_TASK_FAILED', or 'ALREADY_CALLED'\n"
            "- Resume: Look for 'RESUME_GENERATION_COMPLETED', 'RESUME_GENERATION_FAILED', or 'ALREADY_CALLED'\n\n"
            "CALL PROTECTION RESPONSES:\n"
            "- 'ALREADY_CALLED': Agent was previously executed, use existing results\n"
            "- 'CALL_BLOCKED': Concurrent execution prevented, acknowledge and continue\n\n"
            "Remember: Each agent has built-in protection against multiple calls. Respect these safeguards."
        ),
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile()
    
    return supervisor

# ===============================
# ENHANCED MAIN EXECUTION FUNCTION
# ===============================
async def generate_resume_workflow(
    github_url: Optional[str] = None,
    portfolio_url: Optional[str] = None, 
    job_description: Optional[str] = None,
    old_resume_text: Optional[str] = None,
    user_feedback: Optional[str] = None,
    user_additions: Optional[str] = None
):
    """Execute the complete resume generation workflow with single-call protection"""
    
    try:
        # Reset tracker for new workflow
        await call_tracker.reset()
        
        # Build input summary for logging
        inputs_provided = []
        if github_url: inputs_provided.append("GitHub URL")
        if portfolio_url: inputs_provided.append("Portfolio URL")
        if job_description: inputs_provided.append("Job Description")
        if old_resume_text: inputs_provided.append("Old Resume Text")
        if user_feedback: inputs_provided.append("User Feedback")  
        if user_additions: inputs_provided.append("User Additions")
        
        # Create the user request message
        user_request = f"""Please generate a comprehensive resume using these inputs with SINGLE-CALL PROTECTION:

📋 AVAILABLE INPUTS:
{', '.join(inputs_provided) if inputs_provided else 'None provided'}

🛡️ SINGLE-CALL PROTECTION ACTIVE:
- Each agent can only be called ONCE
- Monitor for ALREADY_CALLED and CALL_BLOCKED responses
- Do not retry agents that have already been executed

📝 DETAILS:
- GitHub URL: {github_url or 'Not provided'}
- Portfolio URL: {portfolio_url or 'Not provided'}
- Job Description: {'Provided ✓' if job_description else 'Not provided ✗'}
- Old Resume Text: {'Provided ✓' if old_resume_text else 'Not provided ✗'}  
- User Feedback: {user_feedback or 'Not provided'}
- User Additions: {user_additions or 'Not provided'}

🎯 TASK: Please coordinate the workflow to:
1. Process all available inputs using appropriate specialized agents (assign each task ONLY ONCE)
2. Wait for each agent to complete before proceeding
3. Generate a final comprehensive resume using all collected data
4. Respect single-call protection - do not retry agents

📄 JOB DESCRIPTION CONTENT:
{job_description if job_description else 'No job description provided'}

📄 OLD RESUME CONTENT:
{old_resume_text if old_resume_text else 'No old resume provided'}
"""
        
        # Create supervisor and run workflow
        supervisor = create_resume_generation_supervisor()
        
        print("🚀 Starting Resume Generation Supervisor Workflow with Single-Call Protection")
        print(f"📊 Processing: {', '.join(inputs_provided) if inputs_provided else 'No inputs'}")
        print("🛡️ Single-call protection: ACTIVE")
        print("=" * 60)
        
        # Execute the workflow with timeout
        result = await asyncio.wait_for(
            supervisor.ainvoke({
                "messages": [{"role": "user", "content": user_request}]
            }),
            timeout=300  # 5 minute timeout
        )
        
        # Get final tracking status
        final_status = await call_tracker.get_status()
        
        print("\n📊 Final Call Tracking Status:")
        print(f"Called Agents: {final_status['called_agents']}")
        print(f"Completed Tasks: {final_status['completed_tasks']}")
        print("\nFinal Workflow Output:", result["messages"][-1].content)
        print("=" * 60)
        print("✅ Resume Generation Workflow Completed with Single-Call Protection!")
        
        return result
        
    except asyncio.TimeoutError:
        error_msg = "❌ Workflow timed out after 5 minutes"
        print(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"❌ Workflow failed: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

# ===============================
# TESTING FUNCTIONS
# ===============================
async def test_single_call_protection():
    """Test the single-call protection mechanism"""
    print("🧪 Testing Single-Call Protection")
    
    # Reset tracker
    await call_tracker.reset()
    
    # Test GitHub agent multiple calls
    github_agent = create_github_agent()
    
    print("\n1️⃣ First call to GitHub agent:")
    result1 = await github_agent.ainvoke({
        "messages": [{"role": "user", "content": "Extract data from https://github.com/octocat"}]
    })
    print("Result 1:", result1["messages"][-1].content)
    
    print("\n2️⃣ Second call to GitHub agent (should be blocked):")
    result2 = await github_agent.ainvoke({
        "messages": [{"role": "user", "content": "Extract data from https://github.com/octocat"}]
    })
    print("Result 2:", result2["messages"][-1].content)
    
    # Check tracking status
    status = await call_tracker.get_status()
    print(f"\n📊 Tracking Status: {status}")

async def test_individual_agents():
    """Test individual agents with single-call protection"""
    
    # Reset tracker for testing
    await call_tracker.reset()
    
    # Test GitHub agent
    github_agent = create_github_agent()
    github_result = await github_agent.ainvoke({
        "messages": [{"role": "user", "content": "Extract data from https://github.com/octocat"}]
    })
    print("GitHub Agent Result:", github_result["messages"][-1].content)
    
    # Test Portfolio agent  
    portfolio_agent = create_portfolio_agent()
    portfolio_result = await portfolio_agent.ainvoke({
        "messages": [{"role": "user", "content": "Scrape https://example-portfolio.com"}]
    })
    print("Portfolio Agent Result:", portfolio_result["messages"][-1].content)
    
    # Test JD Keywords agent
    jd_agent = create_jd_keywords_agent()
    jd_result = await jd_agent.ainvoke({
        "messages": [{"role": "user", "content": "Extract keywords from: Senior Python Developer position requiring Flask, Django, AWS"}]
    })
    print("JD Keywords Agent Result:", jd_result["messages"][-1].content)

# ===============================
# EXAMPLE USAGE & MAIN EXECUTION
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
            old_resume_text=old_resume_sample,
            user_feedback="Highlight my machine learning projects and open source contributions",
            user_additions="Add AWS Solutions Architect certification earned in 2024"
        )
        
        print("\n🎉 Final Result:")
        print(result["messages"][-1].content)
    
    # Uncomment to test single-call protection
    # await test_single_call_protection()
    
    # Uncomment to test individual agents
    # await test_individual_agents()
    
    # Run main workflow
    asyncio.run(main())