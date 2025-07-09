
PLAN_PROMPT="""
<purpose>
    Create a detailed, executable plan for a team of agents to complete a client task, ensuring:
    - Minimal hallucinations
    - Concrete and verifiable tasks
    - Strict, balanced delegation
    - Logical, stepwise flow
    The plan must always start with the Manager (CEO) and end with their final report. The plan must be adaptable to both single and multi-agent teams.
</purpose>

<instructions>
    <instruction>ALWAYS output your plan in the specified XML format, using only the provided team members: {members}.</instruction>
    <instruction>Minimize hallucinations by focusing on concrete, verifiable actions and avoiding ambiguous or speculative language.</instruction>
    <instruction>Distribute tasks strictly and evenly among the available agents. No agent should be overloaded or assigned multiple sequential steps unless absolutely necessary. Prevent self-delegation (an agent communicating with itself).</instruction>
    <instruction>Maintain a logical, stepwise flow of tasks. Each step must naturally follow from the previous one. Prioritize delegation over assigning multiple sequential tasks to one agent where possible.</instruction>
    <instruction>The Manager (CEO) must always initiate and conclude the plan (with a final report).</instruction>
    <instruction>If the team consists of only the Manager, proceed directly to task execution without delegation steps. Clearly explain the rationale for this approach in the <think> section.</instruction>
    <instruction>Do not create new agents or assume their existence. Use only the provided team members: {members}.</instruction>
    <instruction>Never include any agent or step not explicitly listed in {members}.</instruction>
    <instruction>Never use vague, imaginative, or unverifiable steps. Every step must be actionable and concrete.</instruction>
    <instruction>Output the plan in the specified XML format, strictly following the structure in the examples.</instruction>
</instructions>

<examples>
    <example>
        <members>Manager (CEO), Researcher, Writer</members>
        <plan>
            <think>Step 1: The Manager evaluates the client task "Write a blog post about AI." and initiates the plan. Reasoning: The Researcher is best suited for gathering information, and the Writer will create the blog post. The manager will review and submit the final draft.

            Task List:
            - Researcher: Gather relevant information on AI. Expected Outcome: Comprehensive notes on AI.
            - Writer: Write a blog post based on the Researcher's notes. Expected Outcome: A draft blog post.
            - Manager: Review and submit the final blog post. Expected Outcome: A polished and submitted blog post.</think>
            <step>1: Manager delegates research to Researcher.</step>
            <step>2: Researcher gathers information on AI and sends it to the Writer.</step>
            <step>3: Writer drafts the blog post and submits it to the Manager.</step>
            <step>4: Manager reviews and submits the final blog post.</step>
        </plan>
    </example>
    <example>
        <members>Manager (CEO)</members>
        <plan>
            <think>Step 1: The Manager evaluates the client task "Summarize the latest news on quantum computing." and initiates the plan. Reasoning: As the only team member, the Manager will perform all tasks. Since there is only one member, delegation is not possible or necessary. This ensures efficiency and avoids redundant steps.

            Task List:
            - Manager: Research and summarize the latest news on quantum computing. Expected Outcome: A concise summary of quantum computing news.</think>
            <step>1: Manager researches quantum computing news.</step>
            <step>2: Manager summarizes findings.</step>
            <step>3: Manager reports the summary.</step>
        </plan>
    </example>
</examples>

<content>
    <members>{members}</members>
    <client_task>{client_task}</client_task>
</content>
"""

# - If the manager is the only member and then just go straight into the action, since there is a single member which is the manger itself there is no need of any delegation of tasks.