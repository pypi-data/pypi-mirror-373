# PRISM - AI-Powered Image Intelligence Engine

> See what others can't.

## Quick Start

```bash
pip install prism
```

```python
import prism

# Analyze any image
result = prism.analyze("photo.jpg")

print(result.summary)    # "Two people having coffee in urban cafe"
print(result.scene)      # "indoor office meeting"  
print(result.objects)    # ['person', 'person', 'coffee', 'table']
print(f"Confidence: {result.confidence:.2%}")  # "Confidence: 87.34%"
```
