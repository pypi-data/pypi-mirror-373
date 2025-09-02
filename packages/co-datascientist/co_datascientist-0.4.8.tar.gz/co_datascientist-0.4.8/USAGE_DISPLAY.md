# Usage Display Features

## Overview

The Co-DataScientist CLI now includes enhanced usage tracking and display features that show your total cost, remaining money, and usage limits. This helps you monitor your free token consumption and avoid hitting usage limits.

## New CLI Commands

### 🔍 Quick Status Check
```bash
co-datascientist status
```

Shows a quick overview of your usage with:
- Current usage vs. limit
- Remaining balance
- Visual progress bar
- Color-coded status indicators

**Example Output:**
```
🔍 Quick Usage Status:
Used: $0.12 / $0.01
Remaining: $-0.11
Progress: [████████████████████] 1200.0%
🚨 BLOCKED - Free tokens exhausted! Contact support or wait for reset.

💡 Use 'costs' command for detailed breakdown
```

### 💰 Enhanced Costs Command
```bash
co-datascientist costs           # Summary with usage limits
co-datascientist costs --detailed # Full breakdown with limits
```

**Summary Output:**
```
💰 Co-DataScientist Usage Summary:
Total Cost: $0.11551650
Usage Limit: $0.01
Remaining: $-0.11 (1155.2% used)
🚨 Status: BLOCKED - Free tokens exhausted!
   You've used $0.12 of your $0.01 limit.
Total Tokens: 0
Workflows Completed: 2
Last Updated: 2025-06-13T13:25:34.263918

💡 Use '--detailed' flag for full breakdown
```

**Detailed Output:**
```
💰 Co-DataScientist Usage Details:
Total Cost: $0.11551650
Usage Limit: $0.01
Remaining: $-0.11
Usage: 1155.2% of limit
🚨 Status: BLOCKED (limit exceeded)
Total Tokens: 0 (0 input + 0 output)
Workflows: 2
Last Updated: 2025-06-13T13:25:34.263918

📊 Workflow Breakdown:
  4964f6cc... | $0.07623330 | 0 tokens
    Model calls: 5
      • openai/o4-mini-2025-04-16: $0.01486520 (0+0 tokens)
      • openai/o4-mini-2025-04-16: $0.01294150 (0+0 tokens)
      • openai/o4-mini-2025-04-16: $0.01185910 (0+0 tokens)
  03379da0... | $0.03928320 | 0 tokens
    Model calls: 4
      • openai/o4-mini-2025-04-16: $0.01258840 (0+0 tokens)
      • openai/o4-mini-2025-04-16: $0.00926530 (0+0 tokens)
      • openai/o4-mini-2025-04-16: $0.00883630 (0+0 tokens)
```

## Status Indicators

The system uses color-coded indicators to show your usage status:

- 🟩 **GOOD** - Under 50% usage
- 🟦 **MODERATE** - 50-79% usage  
- 🟨 **WARNING** - 80-89% usage
- 🟥 **CRITICAL** - 90-99% usage
- 🚨 **BLOCKED** - Over 100% usage (blocked)

## Usage Limit Handling

### When You Hit the Limit

If you exceed your usage limit while running a workflow, you'll see:

```
🚨 FREE TOKENS EXHAUSTED! 🚨
   Free token usage limit exceeded. You have used $0.12 out of your $0.01 limit.
   Current usage: $0.12
   Limit: $0.01

💡 Check your usage status with: co-datascientist status
💡 View detailed costs with: co-datascientist costs
```

### Error Prevention

The system will:
1. Block new workflows when you're over the limit
2. Show clear error messages with your current usage
3. Provide helpful commands to check your status
4. Guide you on next steps

## API Integration

The frontend now calls these backend endpoints:
- `GET /user/usage_status` - Get usage limits and remaining balance
- `GET /user/costs` - Get detailed cost breakdown
- `GET /user/costs/summary` - Get cost summary

## Testing

Run the test script to verify functionality:
```bash
cd co-datascientist
python test_frontend_usage.py
```

## Configuration

The usage limit is set in the backend configuration:
- Default: $20.00 (production)
- Test environment: $0.01 (for testing)

## Troubleshooting

### Command Not Found
Make sure you're in the correct directory and have installed the package:
```bash
cd co-datascientist
pip install -e .
```

### Connection Errors
If you see connection errors:
1. Check that the backend is running
2. Verify your API token with `--reset-token`
3. Use `--dev` flag for local development

### Status Shows Errors
If status/costs commands show errors:
1. Ensure backend has the latest usage limiting code
2. Check that your token has the right permissions
3. Verify the backend endpoints are working

## Future Enhancements

Planned improvements:
- Real-time usage warnings during workflow execution
- Usage prediction based on current workflow
- Weekly/monthly usage reports
- Usage notifications via email
- Multiple usage tiers for different user types 