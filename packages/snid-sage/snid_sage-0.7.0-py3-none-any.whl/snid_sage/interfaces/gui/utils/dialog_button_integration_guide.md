# Dialog Button Enhancement Integration Guide

## Overview
The Enhanced Dialog Button Manager provides consistent visual feedback and styling for all dialog buttons throughout the SNID SAGE GUI. It implements a unified color system based on button functionality and provides smooth hover/click animations.

## Quick Integration

### 1. Simple Enhancement (Automatic)
For dialogs with standard button patterns, simply add these lines:

```python
# Add to imports
from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_buttons

# Add to dialog __init__ after interface creation
self.button_manager = enhance_dialog_buttons(self)
```

### 2. Preset-Based Enhancement (Recommended)
For better control using predefined button configurations:

```python
# Add to imports
from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset

# Add to dialog __init__ after interface creation
self.button_manager = enhance_dialog_with_preset(self, 'your_dialog_name')
```

### 3. Custom Configuration
For dialogs with special requirements:

```python
from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_buttons

custom_config = {
    'apply_btn': {'type': 'apply', 'size_class': 'normal'},
    'special_btn': {'type': 'neutral', 'size_class': 'small'},
}

self.button_manager = enhance_dialog_buttons(self, custom_button_configs=custom_config)
```

## Button Color System by Meaning

| Button Type | Use Cases | Color |
|-------------|-----------|-------|
| **apply** | Apply, Accept, Continue, Proceed, Run | Green (#22c55e) |
| **secondary** | OK, Confirm, Yes, Done | Blue (#3b82f6) |
| **cancel** | Cancel, Close, No, Remove, Delete | Red (#ef4444) |
| **utility** | Export, Save, Copy, Load, Import | Purple (#8b5cf6) |
| **info** | Help, Info, Show, Instructions | Orange (#f59e0b) |
| **reset** | Reset, Refresh, Clear, Revert | Indigo (#6366f1) |
| **navigation** | Previous, Next, Back, Step | Gray (#6b7280) |
| **neutral** | Hide, Test, Browse, Fetch, Auto | Gray-Blue (#64748b) |

## Size Classes

- **normal**: 24px height, 9pt font (default for dialog buttons)
- **small**: 20px height, 8pt font (utility buttons)
- **icon**: 24x24px square, 10pt font (icon-only buttons)

## Special Button Types

### Toggle Buttons
For buttons that change state (like Precision/Normal sensitivity):

```python
from snid_sage.interfaces.gui.utils.dialog_button_enhancer import setup_sensitivity_toggle_button

# Setup after creating the button manager
setup_sensitivity_toggle_button(
    self.button_manager,
    self.sensitivity_button,
    self._toggle_callback,
    initial_state=False
)
```

### Custom Toggle Buttons
For other toggle behaviors:

```python
self.button_manager.register_toggle_button(
    button=self.custom_toggle,
    toggle_callback=self._on_toggle,
    initial_state=False,
    active_text="Mode: Advanced",
    inactive_text="Mode: Basic",
    active_color="#22c55e",    # Optional custom colors
    inactive_color="#64748b"
)
```

## Available Presets

| Preset Name | Dialogs |
|-------------|---------|
| `configuration_dialog` | Main configuration dialog |
| `analysis_progress_dialog` | Analysis progress dialog |
| `manual_redshift_dialog` | Manual redshift dialog |
| `gmm_clustering_dialog` | GMM clustering dialog |
| `emission_dialog` | Emission line dialog |
| `mask_manager_dialog` | Mask manager dialog |
| `settings_dialog` | Settings dialog |
| `results_dialog` | Results dialog |
| `preprocessing_dialog` | Preprocessing dialog |

## Implementation Steps

### Step 1: Add Imports
Add to the top of your dialog file:

```python
# Enhanced button management
try:
    from snid_sage.interfaces.gui.utils.dialog_button_enhancer import enhance_dialog_with_preset
    ENHANCED_BUTTONS_AVAILABLE = True
except ImportError:
    ENHANCED_BUTTONS_AVAILABLE = False
```

### Step 2: Add Object Names
Ensure your buttons have meaningful object names:

```python
apply_btn = QtWidgets.QPushButton("Apply")
apply_btn.setObjectName("apply_btn")  # Important for enhancement system
```

### Step 3: Add Enhancement Method
Add this method to your dialog class:

```python
def _setup_enhanced_buttons(self):
    """Setup enhanced button styling and animations"""
    if not ENHANCED_BUTTONS_AVAILABLE:
        return
    
    try:
        self.button_manager = enhance_dialog_with_preset(self, 'your_preset_name')
    except Exception as e:
        _LOGGER.error(f"Failed to setup enhanced buttons: {e}")
```

### Step 4: Call Enhancement
Add to your dialog's `__init__` method after interface creation:

```python
self._setup_dialog()
self._create_interface()
self._setup_enhanced_buttons()  # Add this line
```

### Step 5: Remove Old Styling (Optional)
Remove manual button styling since the enhancement system handles it:

```python
# Remove old manual styling like:
# button.setStyleSheet("QPushButton { background: red; }")

# Keep only essential properties:
button.setObjectName("apply_btn")
button.clicked.connect(self._apply)
```

## Best Practices

1. **Consistent Naming**: Use meaningful object names that indicate button function
2. **Preset Usage**: Use presets when available for consistency
3. **Color Meaning**: Follow the color system - green for apply actions, red for cancel, etc.
4. **Size Appropriateness**: Use 'normal' size for primary actions, 'small' for utilities
5. **Error Handling**: Always wrap enhancement setup in try-catch blocks
6. **Cleanup**: The button manager handles cleanup automatically

## Creating New Presets

To add a new preset for your dialog type, edit `dialog_button_enhancer.py`:

```python
'your_dialog_name': {
    'apply_btn': {'type': 'apply', 'size_class': 'normal'},
    'cancel_btn': {'type': 'cancel', 'size_class': 'normal'},
    'help_btn': {'type': 'info', 'size_class': 'small'},
    'special_toggle': {
        'type': 'neutral',
        'size_class': 'normal',
        'is_toggle': True,
        'toggle_state': False
    },
},
```

## Troubleshooting

### Enhancement Not Working
- Check that imports are successful (`ENHANCED_BUTTONS_AVAILABLE = True`)
- Verify button object names are set correctly
- Check logs for error messages

### Buttons Look Wrong
- Verify you're using the correct button type for the action
- Check if manual styling is conflicting (remove old stylesheets)
- Ensure the button has the correct object name

### Toggle Buttons Not Working
- Make sure the toggle button is registered after the button manager is created
- Verify the callback function signature matches expected parameters
- Check that the button has appropriate object name and initial state

## Examples

See the integrated examples in:
- `manual_redshift_dialog.py` - Complete integration with toggle button
- `configuration_dialog.py` - Basic preset usage
- `preprocessing_dialog.py` - Complex dialog with multiple button types
- Enhanced button manager test script (if created)