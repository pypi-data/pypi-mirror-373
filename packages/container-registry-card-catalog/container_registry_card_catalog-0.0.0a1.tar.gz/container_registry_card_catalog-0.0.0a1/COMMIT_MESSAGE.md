fix: resolve registry details panel sync issues and enhance mock mode consistency

## Bug Fixes

### Registry Details Panel Synchronization
- Fix registry details panel showing incorrect information when navigating back from repository/tag views
- Implement screen stack length detection to prevent background row highlighting events from interfering with details panel
- Add comprehensive debug logging to track row highlighting events and screen state transitions
- Ensure details panel only updates when main registry screen is active (stack_length ≤ 1)

### Event Handling Improvements
- Filter row highlighting events based on screen stack depth to prevent cross-screen contamination
- Add delayed screen synchronization using `call_later()` for proper screen resume handling
- Enhance debug logging with screen state information and event source tracking

### Mock Mode Consistency and Repository Count Fixes
- Fix mock mode not updating registry count display when monitored repositories are added
- Implement `_refresh_mock_registry_count()` method for immediate UI updates in mock mode
- Fix repository count calculation to properly de-duplicate monitored repositories already in catalog
- Ensure mock mode behavior matches real registry mode for configuration changes with accurate counting
- Add proper count format `total(monitored)` updates after configuration saves in mock mode
- Correct both real and mock registry logic to avoid double-counting repositories that appear in both catalog and monitored lists

## Technical Details

### Root Cause Analysis
Multiple issues were identified and resolved:

1. **Registry Details Panel Sync**: Registry row highlighting events were continuing to fire in the background while users navigated repository and tag views. These background events were updating the details panel with incorrect registry information, causing the wrong details to display when users returned to the main registry screen.

2. **Repository Count Accuracy**: Both real and mock registry modes were double-counting monitored repositories that already appeared in the catalog, leading to inflated repository counts in the format `total(monitored)`.

### Solution Implementation

#### 1. Event Filtering by Screen State
```python
# Before: Events processed regardless of screen state
def on_data_table_row_highlighted(self, event):
    self.update_details_for_row(event.cursor_row)

# After: Events filtered by screen stack depth
def on_data_table_row_highlighted(self, event):
    screen_stack_length = len(self.app.screen_stack)
    is_main_screen = screen_stack_length <= 1
    
    if is_main_screen:
        self.update_details_for_row(event.cursor_row)
    else:
        # Ignore background events from inactive screens
        debug_logger.debug("Registry row highlighted - ignoring (sub-screen active)")
```

#### 2. Repository Count De-duplication
```python
# Before: Double-counting monitored repos already in catalog
total_count = catalog_count + len(monitored_repos)
repo_count = f"{total_count}({len(monitored_repos)})"

# After: Proper de-duplication logic
monitored_not_in_catalog = [repo for repo in monitored_repos if repo not in catalog_repos]
total_count = catalog_count + len(monitored_not_in_catalog)
repo_count = f"{total_count}({len(monitored_repos)})"
```

### Debug System Enhancements
- Add detailed logging for registry details update requests with row index and registry name
- Track screen stack length and active screen type in debug output
- Log event filtering decisions for troubleshooting navigation issues
- Implement delayed screen sync with `call_later()` for proper initialization timing

## Verification

### Success Criteria
✅ Registry details panel shows correct information when navigating back from repository views  
✅ Background row highlighting events are properly filtered during sub-screen navigation  
✅ Details panel updates immediately when highlighting different registries on main screen  
✅ Screen resume events properly sync details with current cursor position  
✅ Debug logging provides clear visibility into event flow and filtering decisions  
✅ Mock mode registry counts update immediately when monitored repositories are configured  
✅ Mock mode behavior matches real registry mode for configuration changes  

### User Experience Impact
- Eliminates confusing behavior where wrong registry details appeared after navigation
- Ensures consistent and predictable details panel behavior across all navigation patterns
- Maintains proper cursor position preservation while fixing details synchronization
- Provides debugging infrastructure for future navigation issue troubleshooting
- Mock mode now provides realistic testing experience with immediate configuration feedback
- Consistent behavior between mock and real registry modes for better development workflow

## Files Modified
- **container_registry_card_catalog.py**
  - Enhanced `on_data_table_row_highlighted()` with screen stack filtering
  - Added comprehensive debug logging to `update_details_for_row()`
  - Improved `_sync_details_with_cursor()` with delayed execution and focus management
  - Updated screen resume handlers for better synchronization timing
  - Implemented `_refresh_mock_registry_count()` for mock mode configuration updates
  - Fixed repository count calculation with proper de-duplication logic
  - Added application title "Container Registry Card Catalog - Beta"

- **registry_client.py**
  - Fixed repository count calculation in `check_registry_status()` to avoid double-counting
  - Implemented proper de-duplication logic matching repository fetching behavior

- **README.md**
  - Added comprehensive screenshot gallery with 8 images showing complete user workflow
  - Screenshots cover: main view, repository browser, filtering, tag explorer, tag details, configuration, debug console, and API call details
  - Updated mock mode documentation to reflect accurate repository counting
  - Enhanced feature descriptions with visual documentation

This resolves critical navigation and counting issues while providing comprehensive visual documentation of all application features.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
Vibe-Coder: Andrew Potozniak <potozniak@redhat.com>