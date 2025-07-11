
PLAN_PROMPT = """# Strategic Team Planning Instructions

## Planning Objective
Create a comprehensive, executable plan for the team to complete the client task efficiently and effectively, with minimal redundancy and optimal resource utilization.

## Client Task
**Objective:** {client_task}

## Available Team Members
**Team Composition:** {members}

## Planning Principles
### Core Requirements
1. **Concrete & Actionable** - Every step must be specific and executable
2. **Balanced Delegation** - Distribute tasks evenly based on agent expertise
3. **Logical Sequence** - Each step should naturally flow from the previous one
4. **Manager-Centric** - Plan must start and end with Manager coordination
5. **No Self-Delegation** - Agents cannot delegate tasks to themselves

### Quality Standards
- **Minimize Hallucinations** - Base all planning on factual, verifiable actions
- **Prevent Overloading** - No agent should receive multiple sequential tasks unless necessary
- **Ensure Collaboration** - Foster teamwork and knowledge sharing
- **Maintain Focus** - Keep all activities aligned with the client objective

## Response Format
### MANDATORY: XML Structure
```xml
<plan>
    <think>
        [Detailed strategic analysis explaining your approach]
        - Task breakdown and rationale
        - Agent assignment justification
        - Expected outcomes for each step
        - Risk considerations and mitigation
    </think>
    <step>1: [Specific action with agent assignment]</step>
    <step>2: [Next logical action with agent assignment]</step>
    <step>3: [Continue sequence...]</step>
    <step>N: [Final step - Manager delivers results]</step>
</plan>
```

## Planning Framework
### Strategic Analysis Process
1. **Task Decomposition** - Break down the client objective into manageable components
2. **Skill Mapping** - Match task requirements to available agent expertise
3. **Workflow Design** - Create logical sequence of activities
4. **Resource Allocation** - Ensure balanced workload distribution
5. **Quality Assurance** - Plan for review and validation steps

### Team Coordination Strategy
- **Information Flow** - Plan for effective data and insight sharing between agents
- **Dependency Management** - Identify and sequence interdependent tasks
- **Progress Tracking** - Include checkpoints and status updates
- **Risk Mitigation** - Anticipate potential issues and plan alternatives

## Planning Examples

### Multi-Agent Team Example
**Team:** Manager (CEO), Researcher, Data_Analyst, Writer
**Task:** Create comprehensive market analysis report

```xml
<plan>
    <think>
        Strategic Analysis: The client needs a comprehensive market analysis report. This requires data gathering, analysis, and professional presentation.
        
        Task Breakdown:
        - Research: Market data collection and competitor analysis (Researcher expertise)
        - Analysis: Data processing and insight generation (Data_Analyst expertise)  
        - Documentation: Professional report creation (Writer expertise)
        - Coordination: Quality assurance and delivery (Manager oversight)
        
        Agent Assignment Rationale:
        - Researcher: Best equipped for market intelligence gathering
        - Data_Analyst: Specialized in quantitative analysis and trend identification
        - Writer: Expert in professional documentation and presentation
        - Manager: Strategic oversight and final quality control
        
        Expected Outcomes:
        - Comprehensive market data and competitive landscape
        - Statistical analysis with actionable insights
        - Professional report meeting client standards
    </think>
    <step>1: Manager initiates project and delegates market research to Researcher</step>
    <step>2: Researcher gathers market data and competitor information, sends findings to Data_Analyst</step>
    <step>3: Data_Analyst processes research data and generates statistical insights, forwards analysis to Writer</step>
    <step>4: Writer creates comprehensive report using research and analysis, submits draft to Manager</step>
    <step>5: Manager reviews final report and delivers to client</step>
</plan>
```

### Single Manager Team Example
**Team:** Manager (CEO) only
**Task:** Summarize recent technology trends

```xml
<plan>
    <think>
        Strategic Analysis: Client requests technology trend summary. Since Manager is the only team member, all tasks must be executed independently without delegation.
        
        Approach Rationale:
        - No delegation possible with single member team
        - Manager must handle research, analysis, and documentation
        - Focus on efficiency and direct execution
        
        Expected Outcome:
        - Concise, well-researched technology trend summary
    </think>
    <step>1: Manager researches current technology trends and developments</step>
    <step>2: Manager analyzes findings and identifies key patterns</step>
    <step>3: Manager compiles comprehensive summary and delivers to client</step>
</plan>
```

## Quality Assurance Checklist
### Pre-Submission Validation
- [ ] Every step is concrete and actionable
- [ ] Task distribution is balanced among team members
- [ ] No agent is assigned to communicate with themselves
- [ ] Plan follows logical sequence from start to finish
- [ ] Manager initiates and concludes the plan
- [ ] All team members are effectively utilized
- [ ] No speculative or vague instructions included

### Strategic Considerations
- **Team Size Adaptation** - Plan complexity should match team capacity
- **Expertise Utilization** - Maximize each agent's specialized skills
- **Efficient Communication** - Minimize unnecessary information transfers
- **Result Focus** - Every step should contribute to the final objective

## Critical Reminders
- **Use ONLY provided team members** - Do not create or assume additional agents
- **Maintain logical flow** - Each step should enable the next step
- **Prevent bottlenecks** - Avoid creating dependencies that could delay progress
- **Focus on deliverables** - Ensure every step produces tangible value
- **Plan for success** - Design workflow that maximizes probability of excellent results"""