"""Test inline JavaScript in HTML widget"""

import ipywidgets as widgets
from IPython.display import display

# Create an HTML widget with inline JavaScript
html_content = '''
<div id="test-div">Click me!</div>
<script type="text/javascript">
document.getElementById('test-div').addEventListener('click', function() {
    alert('Clicked!');
    this.innerHTML = 'Clicked at ' + new Date().toLocaleTimeString();
});
console.log('JavaScript is running!');
</script>
'''

# Display using widgets.HTML
html_widget = widgets.HTML(value=html_content)
display(html_widget)

print("If you see 'Click me!' above and can click it, JavaScript is working.")