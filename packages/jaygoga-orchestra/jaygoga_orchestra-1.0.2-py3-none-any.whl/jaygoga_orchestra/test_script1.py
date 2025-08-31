
from jaygoga_orchestra.v2 import Agent, Team
from jaygoga_orchestra.v2.models.google import Gemini


# Create intelligent agents with advanced capabilities
gemini_agent = Agent(
    name="Gemini_2.5_BlogMaster",
    description="AI agent specialized in blog generation using advanced NLP capabilities of Gemini 2.5",
    instructions="You are a creative AI with a focus on generating engaging, SEO-optimized blog posts based on provided topics.",
    model=Gemini(id="gemini-2.5-flash",api_key="AIzaSyDqH-mCa_2zvZEfYGd5oKlqxGKYybFOLWg")
)

# Create dynamic team with shared context
blog_team = Team(
    members=[gemini_agent],
    name="Blog Generation Unit",
    description="Specialized team for high-quality blog creation",
    mode="collaborate",
    enable_agentic_context=True,
    model=Gemini(id="gemini-2.5-flash",api_key="AIzaSyDqH-")
)

# Execute team for blog generation
blog_team.print_response(
    message="Generate a blog post about 'The Future of AI in Business' with keywords: AI, business transformation, technology trends. Target audience: business professionals. Tone: informal.",
)

