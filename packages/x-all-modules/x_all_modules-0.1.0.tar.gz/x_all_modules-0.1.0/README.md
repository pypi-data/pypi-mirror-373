# x

**Author:** Ashutosh Dwivedi  
**Email:** iasashutosh17@gmail.com  
**License:** CC BY-NC 4.0 + Custom Restrictions  

---

## 📖 Description
`x` is a Python package designed to simplify imports.  
Instead of importing many standard modules separately, you only need to import `x`.  

Every standard Python module is automatically available with the prefix `x_`.  
Special Rules: 
Modules with __ in their name → use x__name (e.g., __future__ → x__future__).

Modules with both _name and name variants → use x_name and x__name respectively (e.g., asyncio → x_asyncio, _asyncio → x__asyncio).

For example:
```python
import x

print(x_math.pi)      # from math module
x_sys.exit()          # from sys module
