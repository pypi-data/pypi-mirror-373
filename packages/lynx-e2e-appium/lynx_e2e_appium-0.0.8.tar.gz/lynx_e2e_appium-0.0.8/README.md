## What is lynx-e2e?

lynx-e2e is a UI automation framework customized for Lynx.

You will utilize the following capabilities through lynx-e2e:

- **Cross Platform:** Write end-to-end tests in Python for apps using Lynx (Android & iOS).
- **Test Management:** Lynx-E2E provides testcase managment ability. You can control the specific list of test cases for each run.
- **Inspect Lynx:**  Through Lynx-E2E, you can search for, locate and operate any node in LynxView.

## What Does a lynx-e2e Test Look Like?

This is a test for performing click operations on a simple Lynx demo page:

```python
from lynx_e2e.api.app import LynxApp as LynxAppBase
from lynx_e2e.api.lynx_view import LynxView
from lynx_e2e.api.testcase import TestCase

class DemoTest(TestCase):
    def pre_test(self):
        self.start_step('--------Aquire Device--------')
        self.device = self.acquire_device()
        app = LynxApp(self.device)
        self.app = app
        super().pre_test()

    def run_test(self, test=None):
        self.app.connect_app_to_lynx_server()
        time.sleep(2)
        self.app.open_card("sslocal://lynxtest?local://automation/core/initData/template.js?width=720&height=1280&density=320")
        lynxview = self.app.get_lynxview('lynxview', LynxView)

        count = lynxview.get_by_test_tag("count")
        button = lynxview.get_by_test_tag("button")
        button.click()
        test.wait_for_equal('setData failed', count_view, 'text', '1')

class LynxApp(LynxAppBase):
    app_spec = {
        "package_name": "com.lynx.example",  # app package name
        "init_device": True,  # whether to wake up device
        "process_name": "",  # main process name of app
        "start_activity": "com.lynx.example.LynxViewShellActivity",  # leave it empty to be detected automatically
        "grant_all_permissions": True,  # grant all permissions before starting app
        "clear_data": False,  # pm clear app data
        "kill_process": True  # whether to kill previously started app
    }

    def __init__(self, *args, **kwargs):
        kwargs['app_spec'] = self.app_spec
        super(LynxApp, self).__init__(*args, **kwargs)

    def open_card(self, url):
        if url == '':
            return
        self.open_lynx_container(url)

if __name__ == '__main__':
    DemoTest().debug_run()
```

## Using Guides

### 1. Import lynx-e2e

You can introduce the following dependencies in the requirements.txt of the project.

```python
# lynx-e2e
lynx-e2e-appium
# appium dependencies
appium-python-client==3.1.1
selenium==4.17.2
```

### 2. Set App Base Info

You need to inherit from the LynxApp class and set the basic information of the app under test in it, such as the packageName and so on.

```python
from lynx_e2e.api.app import LynxApp as LynxAppBase

class LynxApp(LynxAppBase):
    app_spec = {
        "package_name": "com.lynx.example",  # app package name
        "start_activity": "com.lynx.example.LynxViewShellActivity",  # leave it empty to be detected automatically
    }

    def __init__(self, *args, **kwargs):
        kwargs['app_spec'] = self.app_spec
        super(LynxApp, self).__init__(*args, **kwargs)
```

These basic pieces of information will be converted by the Lynx-e2e framework into AppiumOptions recognized by Appium.

### 3. Locate LynxView

You can use get_lynxview method from LynxApp to get the LynxView instance.
```python
from lynx_e2e.api.lynx_view import LynxView
lynxview = app.get_lynxview('lynxview', LynxView)
```

### 4. Search Element in LynxView

We provide multiple methods for element location, such as by text, class, test_tag, etc. Among them, the test-tag is provided internally by Lynx and is used to provide a custom unique identifier for the internal elements of LynxView.

All of the above methods are encapsulated in the LynxView object and can be directly called through the LynxView object. See the list of methods from [search method](https://github.com/lynx-infra/lynx-e2e/blob/main/lynx_e2e/_impl/appium/lynx_view.py#L35)

## Project structure

Next, the structure of the project engineering will be introduced.

```python
.
|_____impl
| |____testcase
| | |____testcase.py
| | |____retry.py
| | |____testcase_context.py
| |____exception.py
| |____config.py
| |____core # Implementation of core functions.
| | |____net # Communicate with LynxDevtool through socket.
| | | |____usb_connector.py
| | | |____sender.py
| | | |____base_connector.py
| | | |____receiver.py
| | |____upath.py
| | |____logger
| | | |____cdp_logger.py
| | | |____console_logger.py
| | |____element_searcher.py
| | |____document_tree.py
| | |____debugger.py
| | |____lynx_driver.py
| | |____utils.py
| | |____debugger_mixin # Capability enhancements based on Devtool, including taking screenshots, test bench recording and playback, etc.
| | | |____screencast.py
| | | |____testbench.py
| | | |____runtime.py
| | | |____performance.py
| | | |____dom.py
| | |____lynx_element_mixin.py
| | |____rectangle.py
| | |____app.py
| | |____lynx_view_mixin.py
| |____utils.py
| |____manage # Used for test case management and outputting the results of test runs.
| | |____test_result.py
| | |____exception.py
| | |____case_runner.py
| | |____loader.py
| | |____management.py
| | |____report.py
| |____device 
| | |____exception.py
| | |____android_device_driver_mixin.py
| | |____device.py
| | |____resource.py
| | |____adb
| | | |____exception.py
| | | |____adb_client.py
| | | |____adb.py
| | |____device_driver.py
| |____appium
| | |____device.py
| | |____lynx_element.py
| | |____device_driver.py
| | |____lynx_view.py
| | |____app.py
|____api  # It contains all the callable objects encapsulated for the automation scripts.
| |____exception.py
| |____upath.py
| |____config.py
| |____testcase.py
| |____logger.py
| |____lynx_driver.py
| |____lynx_element.py
| |____lynx_view.py
| |____management.py
| |____app.py
```
