# 🔑 Claude API Key Setup - REQUIRED FOR FULL FUNCTIONALITY

## ❌ Current Issue

The error you're seeing:
```
Error code: 401 - authentication_error: invalid x-api-key
```

This means AutoPurple can't access Claude Haiku for intelligent analysis. **You need a real Claude API key!**

## ✅ How to Fix This

### Step 1: Get a Claude API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys" 
4. Create a new API key
5. Copy the key (starts with `sk-ant-api...`)

### Step 2: Configure the Key

**Option A: Environment Variable (Recommended)**
```bash
export CLAUDE_API_KEY="sk-ant-api-your-actual-key-here"
```

**Option B: Update .env file**
```bash
echo "CLAUDE_API_KEY=sk-ant-api-your-actual-key-here" >> .env
```

**Option C: Direct CLI usage**
```bash
CLAUDE_API_KEY="sk-ant-api-your-actual-key-here" python3 -m autopurple.cli.main run --region us-east-1 --no-dry-run
```

### Step 3: Verify Setup

```bash
# Test the key works
python3 -c "
import os
import anthropic

api_key = os.environ.get('CLAUDE_API_KEY')
if not api_key:
    print('❌ No API key found')
    exit(1)

if api_key.startswith('your-'):
    print('❌ Please use a real API key, not placeholder')
    exit(1)

try:
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model='claude-3-5-haiku-20241022',
        max_tokens=10,
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    print('✅ Claude API key works!')
except Exception as e:
    print(f'❌ API key error: {e}')
"
```

## 🎯 What You're Missing Without Claude

**Current State (Fallback Mode):**
- ✅ ScoutSuite discovery works
- ✅ Pacu validation works  
- ✅ MCP server integration works
- ❌ **Basic/mock analysis only**
- ❌ **No intelligent prioritization**
- ❌ **No expert remediation planning**

**With Claude API Key:**
- ✅ All of the above PLUS:
- ✅ **Expert AWS security analysis**
- ✅ **Risk-based finding prioritization**  
- ✅ **Intelligent attack vector assessment**
- ✅ **Production-ready remediation plans**
- ✅ **Business impact evaluation**
- ✅ **Compliance framework consideration**

## 🚀 Expected Results After Fix

```bash
# Run with proper Claude key
python3 -m autopurple.cli.main run --region us-east-1 --no-dry-run --verbose

# You should see:
✅ Claude analysis completed: Expert security assessment
✅ Intelligent prioritization: Risk-based ranking  
✅ Remediation planning: Production-ready strategies
✅ Business impact: Compliance and operational considerations
```

## 💰 Claude API Pricing

- **Very affordable** for security automation
- **Pay per token** (input + output)
- **Haiku model** is the most cost-effective
- **Typical AutoPurple run**: $0.01-0.05 per scan

## 🔐 Security Note

- Keep your API key secure
- Don't commit it to version control
- Use environment variables in production
- Monitor usage in Anthropic Console

**Fix this to unlock AutoPurple's full intelligent capabilities!** 🧠✨
