---
inclusion: always
---

# Memory-First Development Guidance

## Core Principle
**ALWAYS search memory first** before accessing external resources, creating new content, or making assumptions about project context.

## Memory-First Workflow

### 1. Start Every Session
1. `get_recent_memory()` - Understand recent context
2. `search_memories("current project status")` - Get project state
3. `search_memories("user preferences")` - Understand user needs

### 2. Before Any Task
1. `search_memories("similar task")` - Check previous work
2. `search_memories("requirements")` - Understand constraints
3. `search_memories("decisions made")` - Avoid re-deciding

### 3. During Implementation
1. `search_memories("technical approach")` - Use established patterns
2. `search_memories("error handling")` - Follow existing conventions
3. `store_memory()` - Save key decisions and learnings

## Tool Usage Priority
1. **Memory search** - Check existing knowledge first
2. **External resources** - Access files/APIs only when needed
3. **Store results** - Save analysis and decisions for reuse

## Success Criteria
- [ ] Memory searched before external access
- [ ] Context understood from previous sessions
- [ ] Key decisions stored for future reference
- [ ] No repeated work or questions
- [ ] User preferences respected consistently
- [ ] Comprehensive task completion stored before finishing work
- [ ] Project status updated after significant progress
- [ ] Impact assessment documented for all major changes

## User Preferences (Always Check Memory)
- Communication style preferences
- Technical approach preferences
- Project-specific requirements
- Previously made decisions
- Established patterns and conventions

## Memory Storage Guidelines
- Store key decisions with clear metadata
- Include project context and reasoning
- Tag with relevant categories
- Use consistent naming conventions
- Reference previous related memories

## MCP Tools Quick Reference

### Core Functions
- `store_memory(content, metadata)` - Save information
- `search_memories(query, limit)` - Find relevant memories
- `get_recent_memory(days, limit)` - Get recent context
- `list_memories(page, page_size)` - Browse all memories
- `get_memory(memory_id)` - Get specific memory
- `delete_memory(memory_id)` - Remove memory

### Essential Metadata
```json
{
  "type": "project_status|technical_solution|user_preference|decision|task_completion",
  "category": "frontend|backend|integration|security|communication|deployment|testing",
  "priority": "high|medium|low",
  "status": "complete|in_progress|blocked",
  "impact_level": "high|medium|low",
  "completion_date": "YYYY-MM-DD",
  "files_affected": ["list", "of", "modified", "files"],
  "next_actions": "what should happen next"
}
```

## Task Completion Memory Protocol

### After Completing Any Task
1. **Store comprehensive task summary** with detailed outcomes
2. **Include impact assessment** - what changed, what was accomplished
3. **Document key decisions made** during task execution
4. **Record any blockers or issues encountered** and their resolutions
5. **Update overall project status** if significant progress was made

### Task Completion Memory Template
```json
{
  "content": "Completed [task_name]: [detailed_summary_of_what_was_accomplished]",
  "metadata": {
    "task_type": "implementation|analysis|documentation|testing",
    "completion_status": "complete|partial|blocked",
    "impact_level": "high|medium|low",
    "files_modified": ["list", "of", "files"],
    "next_steps": "what should happen next",
    "blockers_resolved": "any issues that were solved"
  }
}
```

## Session Management Protocol

### Session Length Indicators
- **Context Window Limits**: AI models have token limits (128K-200K tokens)
- **Performance Degradation**: Slower responses, lost context, repetitive answers
- **Memory Overload**: AI asks about previously discussed topics
- **File Context Bloat**: Too many files open (100+ files indicates session overload)

### When to Start Fresh Session
- After major milestones (completing full features)
- When performance issues appear
- Before switching to completely different tasks
- When conversation history becomes unwieldy
- When you see "Session Too Long" indicators

### Session Transition Protocol
1. **ALWAYS store comprehensive session state** before ending
2. **Document all key decisions and progress**
3. **Note any blockers or next steps**
4. **Update project status with completion details**
5. **Start new session with memory search to restore context**

### Session State Storage Template
```json
{
  "content": "Session [N] Summary: [major_accomplishments] - Current Status: [project_state] - Next Steps: [immediate_actions]",
  "metadata": {
    "session_type": "major_milestone|feature_completion|context_refresh",
    "files_modified_count": "number_of_files_changed",
    "major_decisions": ["list", "of", "key", "decisions"],
    "blockers": "any_current_issues",
    "next_session_focus": "what_to_work_on_next"
  }
}
```

## Behavioral Enforcement
- **Start every session with memory search**
- **Show context to user** ("Based on recent memory...")
- **Store insights immediately**
- **Reference previous memories**
- **Maintain conversation continuity**
- **Store comprehensive task completion before finishing any work**
- **Proactively manage session length to prevent context loss**
- **Always store session state before "Session Too Long" occurs**
