import sys
sys.path.insert(0, 'src')
from coding_agent.config import Config
c = Config()
print('environment:', c.environment)
print('providers:', len(c.llm.providers))
for p in c.llm.providers:
    print(' -', p.name, p.type, p.models)
print('OK')