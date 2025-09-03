━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ❗ 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 𝗡𝗢𝗧𝗜𝗖𝗘

**Your use of this Software in any form constitutes your acceptance of this Agreement.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

>>pip install SyloraQ
>>>Run this so u can use the library. 

```bash
pip install SyloraQ
```

### Note on imports and the 🛡️ symbol:

> If a function or class has the (🛡️) symbol:  
>> Import it with `from SyloraQ.security import function_or_class`  
> Otherwise:  
>> Import with `from SyloraQ import *`

The nested symbols like 🛡️i or 🛡️i+ indicate layers of insideness (inside functions/classes of 🛡️ items), extending as needed.

### Note on imports and the 🌐 symbol:

> If a function or class has the (🌐) symbol:  
>> Import it with `from SyloraQ.web import function_or_class`

The nested symbols like 🌐i or 🌐i+ indicate layers of insideness (inside functions/classes of 🛡️ items), extending as needed.

### Your use of this Software in any form constitutes your acceptance of this Agreement.

> **`wait(key="s", num=1)`**  
>> Pauses execution for a specified amount of time. The unit is controlled by the `key` parameter, which can be 's' for seconds, 'm' for minutes, or 'h' for hours.

> **`ifnull(value, default)`**  
>> Checks if the given `value` is missing or empty. Returns `default` if so, otherwise returns the original `value`.

> **`switch_case(key, cases, default=None)`**  
>> Looks up the `key` in the `cases` dictionary. If found, returns the corresponding value. If the value is callable (like a function), executes it. Returns `default` if `key` not found.

> **`timer_function(func, seconds)`**  
>> Executes the function `func` after waiting for `seconds`.

> **`iftrue(var, function)`**  
>> Calls `function` only if `var` is `True`.

> **`iffalse(var, function)`**  
>> Calls `function` only if `var` is `False`.

> **`replace(string, replacement, replacement_with)`**  
>> Replaces occurrences of `replacement` in `string` with `replacement_with`.

> **`until(function, whattodo)`**  
>> Repeatedly executes `whattodo()` until `function()` returns `True`.

> **`repeat(function, times)`**  
>> Executes `function` a specified number of `times`.

> **`oncondit(condition, function_true, function_false)`**  
>> Executes `function_true` if `condition` is `True`, otherwise executes `function_false`.

> **`repeat_forever(function)`**  
>> Continuously executes `function` indefinitely.

> **`safe_run(func, *args, **kwargs)`**  
>> Runs `func` safely by catching and printing exceptions if they occur.

> **`start_timer(seconds, callback)`**  
>> Calls `callback` after waiting for `seconds`.

> **`generate_random_string(length=15)`**  
>> Generates a random string of alphanumeric characters and symbols of specified `length`.

> **`get_ip_address()`**  
>> Returns the local IP address of the machine.

> **`send_email(subject, body, to_email, mailname, mailpass)`**  
>> Sends an email via Gmail SMTP. Requires Gmail username (`mailname`) and password (`mailpass`).

> **`generate_unique_id()`**  
>> Generates and returns a unique ID using the `uuid` module.

> **`start_background_task(backtask)`**  
>> Runs the function `backtask` in a separate thread to run it in the background.

> **`nocrash(func)`**  
>> Decorator that wraps `func` to catch and log errors, preventing crashes.

> **`parallel(*functions)`**  
>> Runs multiple `functions` concurrently in separate threads.

> **`gs(func)`**  
>> Returns the source code of the function `func` as a string.

> **`Jctb(input_string)`**  
>> Converts a string into a binary representation, where each character is encoded as a 10-bit binary number.

> **`Jbtc(binary_input)`**  
>> Converts a binary string (produced by `Jctb`) back to the original string.

> **`encode_base64(data)`**  
>> Encodes a string `data` into Base64.

> **`decode_base64(encoded_data)`**  
>> Decodes a Base64 encoded string back to the original string.

> **`reverse_string(string)`**  
>> Reverses the input `string`.

> **`calculate_factorial(number)`**  
>> Recursively calculates the factorial of `number`.

> **`swap_values(a, b)`**  
>> Swaps the values of `a` and `b` and returns the swapped values.

> **`find_maximum(numbers)`**  
>> Finds and returns the maximum value in the list `numbers`.

> **`find_minimum(numbers)`**  
>> Finds and returns the minimum value in the list `numbers`.

> **`sum_list(lst)`**  
>> Returns the sum of elements in the list `lst`.

> **`reverse_list(lst)`**  
>> Returns a reversed version of the list `lst`.

> **`is_prime(n)`**  
>> Returns `True` if `n` is a prime number, otherwise returns `False`.

> **`split_into_chunks(text, chunk_size)`**  
>> Splits a string `text` into chunks of size `chunk_size`.

> **`unique_elements(lst)`**  
>> Returns a list of unique elements from the input list `lst`.

> **`calculate_average(numbers)`**  
>> Returns the average of a list of numbers.

> **`calculate_median(numbers)`**  
>> Returns the median of a list of numbers.

> **`count_words(text)`**  
>> Counts and returns the number of words in the input string `text`.

> **`count_sentences(text)`**  
>> Counts and returns the number of sentences in the input string `text`.

> **`add_commas(input_string)`**  
>> Adds commas between characters in the input string.

> **`remove_spaces(text)`**  
>> Removes all spaces from the input string `text`.

> **`calculate_square_root(number)`**  
>> Approximates the square root of `number` using the Newton-Raphson method.

> **`find_files_by_extension(directory, extension)`**  
>> Returns a list of files in the directory that have the specified file extension.

> **`get_curr_dir()`**  
>> Returns the current working directory.

> **`check_if_file_exists(file_path)`**  
>> Checks if a file exists at `file_path`.

> **`monitor_new_files(directory, callback)`**  
>> Continuously monitors the directory for new files and calls `callback` whenever new files are added.

> **`get_system_uptime()`**  
>> Returns the system's uptime in seconds.

> **`get_cpu_templinux()`**  
>> Retrieves the CPU temperature on a Linux system.

> **`monitor_file_changes(file_path, callback)`**  
>> Monitors the file for changes and calls `callback` when the file is modified.

> **`write_to_file(filename, content)`**  
>> Writes the `content` to the specified `filename`.

> **`read_from_file(filename)`**  
>> Reads and returns the content of the file specified by `filename`.

> **`parse_json(json_string)`**  
>> Parses a JSON string and returns the corresponding Python object.

> **`create_file_if_not_exists(filename)`**  
>> Creates a file if it doesn't already exist.

> **`create_directory(directory)`**  
>> Creates the specified directory if it doesn't exist.

> **`get_cpu_usage()`**  
>> Returns the current CPU usage percentage using `psutil`.

> **`get_memory_usage()`**  
>> Returns the current memory usage percentage using `psutil`.

> **`create_zip_file(source_dir, output_zip)`**  
>> Creates a ZIP archive of the specified `source_dir`.

> **`extract_zip_file(zip_file, extract_dir)`**  
>> Extracts a ZIP archive to the specified `extract_dir`.

> **`move_file(source, destination)`**  
>> Moves a file from `source` to `destination`.

> **`copy_file(source, destination)`**  
>> Copies a file from `source` to `destination`.

> **`show_file_properties(file_path)`**  
>> Displays properties of a file (size and last modified time).

> **`start_http_server(ip="0.0.0.0", port=8000)`**  
>> Starts a simple HTTP server on the given `ip` and `port`.

> **`stop_http_server()`**  
>> Stops the running HTTP server.

> **`get_server_status(url="http://localhost:8000")`**  
>> Checks if the server at the given URL is up and running.

> **`set_server_timeout(timeout=10)`**  
>> Sets the timeout for server connections.

> **`upload_file_to_server(file_path, url="http://localhost:8000/upload")`**  
>> Uploads a file to a server at the specified URL.

> **`download_file_from_server(file_url, save_path)`**  
>> Downloads a file from the server and saves it to `save_path`.

> **`CustomRequestHandler`**  
>> A custom request handler for the HTTP server that responds to specific paths ("/" and "/status").

> **`start_custom_http_server(ip="0.0.0.0", port=8000)`**  
>> Starts a custom HTTP server using the `CustomRequestHandler`.

> **`set_server_access_logs(log_file="server_access.log")`**  
>> Configures logging to store server access logs.

> **`get_server_logs(log_file="server_access.log")`**  
>> Retrieves and prints the server access logs.

> **`restart_http_server()`**  
>> Restarts the HTTP server.

> **`check_internet_connection()`**  
>> Checks if the system has internet connectivity by pinging `google.com`.

> **`create_web_server(directory, port=8000)`**  
>> Serves the contents of a directory over HTTP on the specified port.

> **`create_custom_web_server(html, port=8000)`**  
>> Serves custom HTML content over HTTP on the specified port.

> **`JynParser(rep)`**  
>> Executes a Python script passed as `rep` in a new context (using `exec()`).

> **`contains(input_list, substring)`**  
>> Checks if the given `substring` exists within any element of `input_list`.

> **`Jusbcam(Device_Name)`**  
>> Scans connected USB devices and checks if `Device_Name` is present in the list of detected devices.

> 81. `claw()`  
>> A customizable HTTP server with:  
>> - Custom HTML & subdomains  
>> - IP and port settings (default `0.0.0.0:8000`)  
>> - Logging control  
>> - Custom 404 page  
>> - Auth token for API  
>> - POST `/api/message` for sending messages

> 82. `ConsoleCam()`  
>> Records and returns changes in the console output for a specific part.

> 83. `prn()`  
>> A faster printing function than standard `print()`.

> 84. `Key(KeyName)`  
>> Simulates keyboard actions:  
>> - `.press()`, `.release()`, `.tap()`  
>> - `.type_text(text)`  
>> - `.press_combo(tuple_of_keys)`

> 85. `copy_to_clipboard(text)`  
>> Copies `text` to system clipboard.

> 86. `count_occurrences(lst, element)`  
>> Counts occurrences of `element` in `lst`.

> 87. `get_curr_time()`  
>> Returns the current date and time in the format `YYYY-MM-DD HH:MM:SS`.

> 88. `is_palindrome(s)`  
>> Checks if the string `s` is a palindrome (same forward and backward).

> 89. `get_min_max(list)`  
>> Returns the minimum and maximum values from the list.

> 90. `is_digits(input)`  
>> Checks if the `input` is a string consisting only of digits.

> 91. `create_dict(keys, values)`  
>> Creates a dictionary by pairing elements from `keys` and `values`.

> 92. `square_number(input)`  
>> Returns the square of the number `input`.

> 93. `get_file_size(file_path)`  
>> Gets the size of the file at `file_path`.

> 94. `find_duplicates(lst)`  
>> Finds and returns duplicate elements from the list `lst`.

> 95. `get_average(list)`  
>> Calculates the average of the numbers in the list.

> 96. `divide(a, b)`  
>> Divides `a` by `b` and handles division by zero.

> 97. `extract_numbers(s)`  
>> Extracts all numbers from the string `s`.

> 98. `BinTrig`  
>> A class with multiple methods to bind various Tkinter window and widget events to custom functions, such as mouse movements, key presses, window resize, focus changes, etc.

> 99. `ByteJar`  
>> Sets/Deletes/Gets Cookies with a 3rd party lightweight program. [Download Link](https://www.mediafire.com/file/cwaa748it4x94jo/ByteJarinstaller.exe/file)

> 100. `letterglue(str="", *substr, str2="")`  
>> Joins strings and substrings into one string.

> 101. `letterglue_creator(word)`  
>> Generates code to convert each letter of a word into variables and joins them using `letterglue`.

> 102. `Baudio("filename=audio_data", mode="Write", duration=5, Warn=True)`  
>> Records audio for a specified duration, saves to a `.Bau` file, returns it or plays it. Requires a lightweight program. Usage: `Baudio(filename="my_recording", mode="Write", duration=5, Warn=True)`

> 103. `Btuple`  
>> A utility class with methods like:  
>> - `.count(*words)` - counts total words  
>> - `.get(index, *words)` - retrieves word at index  
>> - `.exists(item, *words)` - checks existence  
>> - `.first(*words)` - gets first word or error  
>> - `.last(*words)` - gets last word or error

> 104. `isgreater(*nums)`  
>> Compares two numbers; returns `True` if first is greater, else error if input invalid.

> 105. `runwfallback(func, fallback_func)`  
>> Runs `func()`, if it fails runs `fallback_func()` instead.

> 106. `retry(func, retries=3, delay=1)`  
>> Tries running `func()` multiple times with delays. Returns `None` if all attempts fail.

> 107. `fftime(func)`  
>> Measures and prints the execution time of `func()`.

> 108. `debug(func)`  
>> Logs function calls, arguments, and return values for debugging.

> 109. `paste_from_clipboard()`  
>> Retrieves and returns text from the system clipboard.

> 110. `watch_file(filepath, callback)`  
>> Monitors file changes and triggers `callback()` on modification.

> 111. `is_website_online(url)`  
>> Checks if the `url` is reachable; returns `True` if online.

> 112. `shorten_url(long_url)`  
>> Generates and returns a shortened URL.

> 113. `celsius_to_fahrenheit(c)`  
>> Converts Celsius `c` to Fahrenheit.

> 114. `fahrenheit_to_celsius(f)`  
>> Converts Fahrenheit `f` to Celsius.

> 115. `efv(string)`  
>> Parses code string for variables, returns dictionary of variables. Example: `parser = efv("x=5,y=2"); print(parser['y'])` outputs `2`.

> 116. `Hpass(limit=30)`  
>> Generates a strong password of specified length (`limit`).

> 117. `l(input)`  
>> Converts input into a list.

> 118. `dl(input)`  
>> Converts a list input into a string.

> 119. `mix(input)`  
>> Returns a "mix" of the input (details depend on implementation).

> 120. `sugar(input)`  
>> "Sugars" (super salts) the input (details depend on implementation).

> 121. `get_type(value)`  
>> Returns the type and string representation of `value`.

> 122. `Cache` Class  
>> A simple caching system to store and retrieve key-value pairs.

> 123. `cantint(egl, ftw, tw)`  
>> Performs comparisons on values based on provided parameters and clears the `tw` list if certain conditions are met.

> 124. `flatten(obj)`  
>> Flattens a nested list (or iterable) into a single iterable.

> 125. `memoize(func)`  
>> Caches the result of a function to optimize performance.

> 126. `chunk(iterable, size)`  
>> Breaks down a large iterable (e.g., list, string) into smaller chunks of a specified size.

> 127. `merge_dicts(*dicts)`  
>> Merges multiple dictionaries into one.

> 128. `deep_equal(a, b)`  
>> Checks if two objects (lists or dictionaries) are deeply equal.

> 129. `split_by(text, size)`  
>> Splits a string into chunks of a given size.

> 130. `GoodBye2Spy` Class  
>> A class that encapsulates several password and data processing techniques for security-related tasks.

> 131. `Passworded` (Method inside `GoodBye2Spy`)  
>> Provides functionality for creating and verifying password hashes with key mixing and randomization.

> 132. `Shifting` (Method inside `GoodBye2Spy`)  
>> Implements a hashing function that uses bitwise operations on the input data.

> 133. `Oneway` (Method inside `GoodBye2Spy`)  
>> Creates a one-way hashed value using a combination of key mixing and a shifting hash technique.

> 134. `slc(code: str)`  
>> Strips and parses the provided Python code to remove unnecessary line breaks and spaces.

> 135. `AI(text,questions=None,summarize_text=False,summary_length=3)`  
>> It can answer questions or summarize the `text`.

> 136. `GAI` (Method inside `AI`)  
>> It can answer and summarize text. (Better than `summarize` when it comes to QA.)

> 137. `summarize` (Method inside `AI`)  
>> It can summarize text. (Better than `GAI` when it comes to summarizing.)

> 138. `requireADMIN(For windows only!)`  
>> Shuts the program with an error when opened if not run as Administrator.

> 139. `__get_raw_from_web(url)`  
>> Returns the raw text from the raw text `url` (**Module**).

> 140. `@private`  
>> Wraps the function so it can only be used within the class where it's defined.

> 141. `OTKeySystem`  
>> A class that can verify user without needing a database. *Has web version.*

> 142. `creator(timestamp=25)` (Method inside `OTKeySystem`)  
>> Generates one-time usable, location and program reopen proof key.

> 143. `verifier(key,timestamp=25)` (Method inside `OTKeySystem`)  
>> Verifies keys generated by `creator` without any database (`timestamp` must be the same!).

> 144. `remove(input,*chars)`  
>> Removes all elements from `chars` list if they exist in the input text.

> 145. `get_screen_size()`  
>> Returns screen size (width, height).

> 146. `NCMLHS(data: str, shift_rate1=3, shift_rate2=5, rotate_rate1=5, rotate_rate2=7, bits=64)`  
>> Shifts, rotates, shifts, and rotates the data again.

> 147. `remove_duplicates(lst)`  
>> Removes all duplicates from the `lst` list if they exist.

> 148. `uncensor(input)`  
>> Uncensors censored content from the `input` text such as `H311@` to `Hello` (accuracy approx. 85%).

> 149. `BendableLists`  
>> A class for managing multiple named lists that can be created, extended, or queried dynamically.

> 150. `create(list_name)` (Method inside `BendableLists`)  
>> Initializes a new empty list with the specified name, unless it already exists.

> 151. `add(list_name, *elements)` (Method inside `BendableLists`)  
>> Adds one or more elements to the specified list if it exists.

> 152. `remove(list_name, element)` (Method inside `BendableLists`)  
>> Removes a specific element from a named list, if both the list and element exist.

> 153. `get(list_name)` (Method inside `BendableLists`)  
>> Retrieves the contents of a list by name; returns `None` if the list doesn't exist.

> 154. `Nexttime(func, func2)`  
>> Executes `func` the first time it's called, then alternates with `func2` on subsequent calls using a toggled internal state key (`"runnext"`).

> 155. `Http`  
>> A class that can get and post requests to the web.

> 156. `get` (Method inside `Http`)  
>> Returns scraped data from url.

> 157. `post` (Method inside `Http`)  
>> Posts a request to a url and returns the response.

> 158. `getos()`  
>> Returns the OS where the script runs.

> 159. `str2int(input)`  
>> Returns character positions in alphabet based on `input` such as `abc` to `123` or `acb` to `132`.

> 160. `int2str(input)`  
>> Does the opposite of `str2int`.

> 161. `shiftinwin(shiftrate,text)`  
>> Shifts `text` with the rate of `shiftrate` and returns it, e.g., `shiftinwin(5,Hii)` cycles characters.

> 162. `runwithin(code,call,params)`  
>> Runs the `code` calling `class > function()` or `class.function()` with the `params`.

> 163. 🛡️ `Locker`  
>> A class that can lock or unlock a string based on a key (numbers not supported).

> 164. 🛡️i `Lock` (Method inside `Locker`)  
>> Locks the `data` based on `key` and returns it.

> 165. 🛡️i `Unlock` (Method inside `Locker`)  
>> Unlocks the locked data with `key` and returns it.

> 166. `alphabet_shift(text, shiftrate)`  
>> Shifts `text` by the amount of `shiftrate` and returns it, e.g., `"ABC",1` → `"BCD"`.

> 167. `wkint(script, expire=5)`  
>> Waits until `expire` seconds expire. Use `never` as expire for no expiry.

> 168. `countdown(from_to_0)`  
>> Counts down every second and prints until `from_to_0` reaches 0.

> 169. `inviShade`  
>> A class that turns any input into a single invisible character and another that decodes it back to the full original message.

> 170. `encode` (Method inside `inviShade`)  
>> Encodes input text to a single invisible char.

> 171. `decode` (Method inside `inviShade`)  
>> Reverses encoding.

> 172. `boa(string, option, pin)`  
>> Returns `option` from the `pin` in `string`.  
>> Example: `boa("Hello//abc", b or before, "//")` outputs `Hello` because it comes before `//`. If `after`, outputs `abc`.

> 173. 🛡️ `Quasar`  
>> A class that turns any input into a single invisible character and another that decodes it back to the full original message.

> 174. 🛡️i `encode` (Method inside `Quasar`)  
>> Encrypts input.

> 175. 🛡️i `decode` (Method inside `Quasar`)  
>> Reverses encrypting.

> 176. `@time_limited_cache(seconds)`  
>> Like `memoize()` but caches results only for `seconds` period of time.

> 177. `GlowShell`  
>> A utility class that provides styled printing, cursor control, and animated frame playback in the terminal.

> 178. `print(message, fg=None, bg=None, bold=False, underline=False, dim=False, bright=False, blink=False, end="\n")` (Method inside `GlowShell`)  
>> Prints the `message` with given color and style settings. Automatically resets the style after printing.

> 179. `clear()` (Method inside `GlowShell`)  
>> Clears the entire terminal screen and moves the cursor to the top-left corner.

> 180. `clear_line()` (Method inside `GlowShell`)  
>> Clears the current line only, leaving the rest of the terminal untouched.

> 181. `move_cursor(row, col)` (Method inside `GlowShell`)  
>> Moves the terminal cursor to the specified `row` and `column`.

> 182. `hide_cursor()` (Method inside `GlowShell`)  
>> Hides the blinking terminal cursor until shown again.

> 183. `show_cursor()` (Method inside `GlowShell`)  
>> Shows the terminal cursor if it was previously hidden.

> 184. `test()` (Method inside `GlowShell`)  
>> Demonstrates usage of styles, colors, cursor movement, and clearing capabilities. Useful for checking terminal support.

> 185. `animate_frames(frames, ...)` (Method inside `GlowShell`)  
>>     This function displays a sequence of multi-line text frames (like ASCII art) in the terminal, one after the other, with optional looping and formatting like color, bold, delay, etc.
>>>>     --------------------------------------------------------------------------------------------------------------------------------
>>>>     |    Key    |       Description        |                                   Values                                              |
>>>>     |-----------|--------------------------|---------------------------------------------------------------------------------------|
>>>>     | `fg`      | Foreground (text) color  | `"black"`, `"red"`, `"green"`, `"yellow"`, `"blue"`, `"magenta"`, `"cyan"`, `"white"` |
>>>>     | `bg`      | Background color         | Same as `fg` colors                                                                   |
>>>>     | `bold`    | Bold text                | `true` or `false`                                                                     |
>>>>     | `dim`     | Dim text                 | `true` or `false`                                                                     |
>>>>     |`underline`| Underline text           | `true` or `false`                                                                     |
>>>>     | `bright`  | Bright color variation   | `true` or `false`                                                                     |
>>>>     | `blink`   | Blinking text            | `true` or `false`                                                                     |
>>>>     | `delay`   | Delay time for this frame| Any positive number like `0.3`, `1`, etc.  (Seconds)                                  |
>>>>     --------------------------------------------------------------------------------------------------------------------------------
>>>     frames = [
>>>     "--/fg:green,bold:true,delay:1/--\nThis is a green bold frame.",
>>>     "--/fg:yellow,dim:true,delay:0.5/--\nNow it's dim and yellow.",
>>>     "--/fg:red,bg:white,blink:true,delay:0.3/--\nRed on white and blinking."
>>>     ]

> 186. `@lazy_property` 
>> A property decorator that computes a value once on first access and caches it for later use.

> 187. 🌐 `BrowSentinel(headless=True, port=9222)`  
>> High-level browser controller class that manages a headless Chrome instance with remote debugging enabled on the specified port. Provides methods to control browsing, page navigation, interaction, and automation.

> 188. 🌐i `start()` (Method inside `BrowSentinel`)  
>> Launches Chrome with remote debugging enabled, connects to the first available browser page, and enables key domains (`Page`, `DOM`, and `Network`) to prepare for interaction.

> 189. 🌐i `navigate(url)` (Method inside `BrowSentinel`)  
>> Navigates the browser to the specified URL. Returns a response including frame and loader identifiers.

> 190. 🌐 `reload()` (Method inside `BrowSentinel`)  
>> Reloads the current page.

> 191. 🌐 `back()` (Method inside `BrowSentinel`)  
>> Navigates back in the browser history by retrieving the navigation history and navigating to the previous entry.

> 192. 🌐 `forward()` (Method inside `BrowSentinel`)  
>> Navigates forward in the browser history similarly by using navigation history.

> 193. 🌐 `set_viewport(width, height, deviceScaleFactor=1)` (Method inside `BrowSentinel`)  
>> Overrides the viewport size and device scale factor to emulate different screen sizes and pixel densities.

> 194. 🌐 `evaluate(script)` (Method inside `BrowSentinel`)  
>> Executes JavaScript code within the current page context and returns the result value.

> 195. 🌐 `get_html()` (Method inside `BrowSentinel`)  
>> Retrieves the full HTML markup of the current page.

> 196. 🌐 `get_text()` (Method inside `BrowSentinel`)  
>> Retrieves the visible text content of the page (equivalent to `document.body.innerText`).

> 197. 🌐 `click(selector)` (Method inside `BrowSentinel`)  
>> Simulates a mouse click on the first element matched by the given CSS selector.

> 198. 🌐 `type(selector, text)` (Method inside `BrowSentinel`)  
>> Sets the value of the input element matched by the selector and dispatches an input event, simulating user typing.

> 199. 🌐 `wait_for(selector, timeout=5)` (Method inside `BrowSentinel`)  
>> Waits asynchronously until an element matching the selector appears on the page or the timeout is reached.

> 200. 🌐 `screenshot(path="page.png")` (Method inside `BrowSentinel`)  
>> Captures a screenshot of the current page and saves it as a PNG file at the specified path.

> 201. 🌐 `close()` (Method inside `BrowSentinel`)  
>> Closes the browser session and terminates the Chrome process cleanly.

>>    The `BrowSentinel` class provides a minimal yet robust interface for controlling a headless Chrome browser via Chrome DevTools Protocol. It enables navigation, DOM interaction, scripting, viewport control, and screenshot capture all without external dependencies beyond Python’s standard library and a local Chrome installation.

>>    Typical workflow:

>>>    1. Instantiate the browser object: `Browser = BrowSentinel()`
>>>    2. Start the browser and connect: `browser.start()`
>>>    3. Navigate pages, interact with elements, evaluate (run JavaScript in the page), capture screenshots or extract page data
>>>    4. Close when done: `browser.close()`

>>>    Try out this:
>>>
    ```python
    t2s="""
    function replaceTextWithSyloraQ() {
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );

    let node;
    while (node = walker.nextNode()) {
        if (node.nodeValue.trim() !== "") {
        node.nodeValue = "SyloraQ";
        }
    }
    }

    replaceTextWithSyloraQ();
    """

    if __name__ == "__main__":
        b = BrowSentinel()
        print("Starting browser...")
        b.start()
        b.navigate("https://example.com")
        
        
        b.screenshot()
        inp=len(input("Please Check the file then delete it before pressing enter>"))
        if inp-inp==0:
            b.evaluate(t2s)
            b.screenshot()
            b.close
    ```

> 🌐 `api(port)` (Works with `@endpoint()`)  
>> Creates an api server

> 🌐 `@endpoint(name)` (Works with `api()`)  
>> Adds and endpoint to the api server.
>>> Try out this:
    ```python
    import time
    def run_api(port=8381):
        @endpoint("hello")
        def hello_endpoint(body, headers):
            name = body.get("input") if isinstance(body, dict) else None
            if headers.get("Token") == "YourToken":
                return {"message": f"Hello, {name}!"}
            else:
                return {"error": "Sorry, invalid token"}

        api(port=port)

        print(f"API server running on port {port} with endpoint '/api/hello'")
        try:
            while True:time.sleep(10000000)
        except KeyboardInterrupt:
            print("Server stopped.")

    run_api(8381)
    ```
>>> Then run on ur cmd:
    ```bash
    curl -X POST http://localhost:8381/api/hello ^
        -H "Content-Type: application/json" ^
        -H "Token: my-secret-token" ^
        -d "{\"input\":\"Alice\"}"
    ```

> `stick_overlay(tk_win, process_name="Notepad.exe", x_offset=20, y_offset=60, interval=30)`  
>> Creates a dynamic overlay window that tracks the position of the main window of a given process by name, updating the overlay’s position in real-time.

> `similarity(sentence1, sentence2, drama_mode=False)`  
>> Calculates a similarity score between two sentences.

> **`class Jsonify`**  
>> A utility class for advanced JSON manipulation. Supports conversion from strings/files, deep access and modification, merging, validation, searching, and exporting.  
>>
>>> `from_string(json_string)`  
>>>> Parses a JSON string into a `Jsonify` object using `json.loads()`.

>>> `frs(string)`  
>>>> Parses loose or malformed string in the form `"key1:val1,key2:val2"` into a `Jsonify` object.

>>> `from_file(filepath)`  
>>>> Loads JSON from a file and returns a `Jsonify` instance.

>>> `to_string(pretty=False)`  
>>>> Converts the internal JSON data back into a string. If `pretty=True`, outputs formatted JSON.

>>> `to_file(filepath, pretty=False)`  
>>>> Saves the internal JSON to a file. Supports pretty formatting.

>>> `get(key, default=None)`  
>>>> Gets value by dot notation key (`"a.b.c"` or `"a.0.b"` for lists). Returns `default` if not found.

>>> `set(key, value)`  
>>>> Sets value by dot notation key. Creates nested structures if necessary.

>>> `remove(key)`  
>>>> Removes value by dot notation key. Returns `True` if removed, else `False`.

>>> `merge(other)`  
>>>> Deep-merges another `dict` or `Jsonify` into the current data. Keys are recursively updated.

>>> `search(pattern, search_keys=True, search_values=True)`  
>>>> Regex-based search over keys and/or string values. Returns list of matching dot notation paths.

>>> `validate_keys(required_keys)`  
>>>> Ensures all given dot-notation keys exist in data. Returns `True` if all exist.

>>> `copy()`  
>>>> Returns a deep copy of the current `Jsonify` instance.

>>> `clear()`  
>>>> Clears the internal data (dict or list). If another type, resets to empty dict.

> **`class Textify`**  
>> A utility class for applying functions over characters, words, groups, or sentences in a text.
>>
>>> `for_every_char(do)`  
>>>> Applies function `do(char)` to every character in the text.

>>> `for_every_word(do)`  
>>>> Applies function `do(word)` to every word in the text (split by whitespace).

>>> `for_every_group(n, do)`  
>>>> Applies function `do(group)` to each substring group of size `n`.

>>> `for_every_sentence(do)`  
>>>> Applies function `do(sentence)` to each sentence (split using punctuation and space).

>>> `result()`  
>>>> Returns the processed text.

> **`def exists(string, pin)`**  
>> Checks if `pin` exists within `string`.  
>>> Returns `True` if found, else `False`.

> 🌐 **`UrlValidate(url)`**  
>> Validates a URL. (The url must be published on internet!)

> **`def Shut()`**  
>> Suppresses all standard output, error, and logging temporarily.  
>>> Returns a tuple of original output/logging states for restoration.

> **`def UnShut(origins)`**  
>> Restores original stdout, stderr, print, and logging.  
>>> `origins` should be the tuple returned by `Shut()`.

> **`class ZypherTrail`**  
>> Encodes and decodes text using a vertical zigzag (rail fence-like) cipher.

>>> **`encode(string, max_row=5)`**  
>>>> Encodes text in a zigzag pattern up to `max_row`. Returns a multi-line string.

>>> **`decode(encoded_str)`**  
>>>> Decodes the zigzag-encoded string back to its original form.

> **`NLDurationParser(seconds: int, full=False)`**
>> Converts a number of seconds into a human-readable duration string, choosing the largest suitable unit (seconds, minutes, hours, days, or years).
>> When `full` is `True`, uses full unit names; otherwise, uses abbreviations.

> **`justify(words, max_width)`**
>> Formats a list of words into fully justified lines of a given width.
>> Distributes spaces evenly between words, padding the last line with spaces on the right.

> **`draw_tree(path, prefix="")`**
>> Recursively prints a visual tree of directories and files starting from a specified path.
>> Uses branch and indent symbols to represent file system hierarchy.

> **`@prefix(pfx)`**
>> A decorator that scans command-line arguments and calls the decorated function with arguments matching a specific prefix (with the prefix removed).

> **`SQS(path)`**
>> A configuration file manager supporting global keys and named sections.
>> Loads, reads, writes, deletes, toggles, and saves config values, parsing expressions and inline comments.
```sqs
#This is a comment!

# Global variables
debug = true
max_retries = 5
pi_value = 3.14159

# Section with variables
[network]
host = "localhost"
port = 8080

# Conditional assignment
if max_retries >= 3 then retry_mode = "aggressive"

# Toggle a boolean
toggle debug

# Arithmetic operation
max_retries += 2

# Copy value from one key to another
set retry_count to max_retries

# etc.
```

> **`read(key, default=None, section=None)` (Method inside `SQS`)**
>> Retrieves a stored value from the specified section or global scope, returning a default if key is missing.

> **`write(text)` (Method inside `SQS`)**
>> Parses and processes multiple lines of config expressions from a text block, updating internal state.

> **`delete(key, section=None)` (Method inside `SQS`)**
>> Removes a key from a given section or the global config if no section specified.

> **`has_key(key, section=None)` (Method inside `SQS`)**
>> Checks existence of a key in a section or globally.

> **`save()` (Method inside `SQS`)**
>> Writes current global keys and all sections with their keys back to the config file, preserving format.

> **`reload()` (Method inside `SQS`)**
>> Clears internal data and reloads configuration from the file.

>  **`to_dict()` (Method inside `SQS`)**
>> Returns the entire configuration as a nested dictionary with globals and sections.

>  **`PYCify`**
>> Utility class for compiling Python source files into bytecode and loading compiled modules dynamically.

> **`compile(source_path, pyc_path=None)` (Method inside `PYCify`)**
>> Reads a Python source file, compiles it into bytecode, writes the `.pyc` file with correct header info (magic number, timestamp).

> **`load(pyc_path, module_name)` (Method inside `PYCify`)**
>> Loads a compiled `.pyc` file as a Python module by name, enabling dynamic imports from bytecode.

> **`tts(text,gender)`**
>> Plays the audio of a `gender (male/female)` saying `text`.
>> This is a basic `text to speech` so dont expect very much from it. `;)`

> **`Cursor`**
>> Utility class for managing and editing multiline text with cursor navigation, selection, and undo/redo functionality.

> **`move(direction, steps=1)`** *(Method inside `Cursor`)*
>> Moves the cursor in the specified direction (`"u"` up, `"d"` down, `"l"` left, `"r"` right) by the given number of steps.

> **`move_to_start_of_line()`** *(Method inside `Cursor`)*
>> Positions the cursor at the start of the current line.

> **`move_to_end_of_line()`** *(Method inside `Cursor`)*
>> Positions the cursor at the end of the current line.

> **`goto_start()`** *(Method inside `Cursor`)*
>> Moves the cursor to the very beginning of the text.

> **`goto_end()`** *(Method inside `Cursor`)*
>> Moves the cursor to the very end of the text.

> **`goto_line(line_number)`** *(Method inside `Cursor`)*
>> Moves the cursor to the specified line, keeping the column position if possible.

> **`select_all()`** *(Method inside `Cursor`)*
>> Selects the entire text from start to end.

> **`hold()`** *(Method inside `Cursor`)*
>> Starts a text selection at the current cursor position.

> **`release()`** *(Method inside `Cursor`)*
>> Cancels any active text selection.

> **`undo()`** *(Method inside `Cursor`)*
>> Reverts the most recent text change.

> **`redo()`** *(Method inside `Cursor`)*
>> Reapplies an undone change.

> **`trim_trailing_spaces()`** *(Method inside `Cursor`)*
>> Removes trailing whitespace from every line in the text.

> **`replace_all(old, new)`** *(Method inside `Cursor`)*
>> Replaces all occurrences of `old` with `new` across all lines.

> **`get_position()`** *(Method inside `Cursor`)*
>> Returns the current cursor row and column as a tuple.

> **`get_selection_text()`** *(Method inside `Cursor`)*
>> Retrieves the text currently selected, or an empty string if no selection is active.

> **`copy()`** *(Method inside `Cursor`)*
>> Copies the selected text into the internal clipboard.

> **`cut()`** *(Method inside `Cursor`)*
>> Copies the selected text to the clipboard and deletes it from the text.

> **`paste()`** *(Method inside `Cursor`)*
>> Inserts the clipboard contents at the cursor position.

> **`keyboard`** *(Property of `Cursor`)*
>> Provides access to an internal `Keyboard` object offering typing and deletion operations.

> **`Keyboard.type(text)`** *(Method inside `Keyboard`)*
>> Types the provided text at the cursor position, replacing any active selection.

> **`Keyboard.backspace()`** *(Method inside `Keyboard`)*
>> Deletes the character before the cursor or removes the selection if active.

> **`Keyboard.delete()`** *(Method inside `Keyboard`)*
>> Deletes the character after the cursor.

> **`Keyboard.enter()`** *(Method inside `Keyboard`)*
>> Inserts a new line at the cursor position.

> **`Keyboard.delete_selection()`** *(Method inside `Keyboard`)*
>> Deletes the currently selected text region.

> **`HardCache`**
>> Utility class for compressing and storing text content in hidden files on the desktop, supporting retrieval and decompression.

> **`create()`** *(Method inside `HardCache`)*
>> Compresses the content and writes it to a hidden file on the desktop, setting attributes based on the operating system.

> **`read()`** *(Method inside `HardCache`)*
>> Reveals the cached file, decompresses its content, deletes the file, and returns the text.

> **`info()`** *(Static Method inside `HardCache`)*
>> Prints a brief description of the class purpose.

> 🛡️ **`CoLine`**
>> Utility class for encoding and decoding strings arranged in a grid by shifting lines or columns.

> 🛡️i **`encode(input_str, cols, shifttype, line_idx=None, col_idx=None)`** *(Method inside `CoLine`)*
>> Arranges text into a grid of `cols` columns and shifts either a line or a column depending on `shifttype`. Returns the transformed string.

> 🛡️i **`decode(input_str, cols, shifttype, line_idx=None, col_idx=None)`** *(Method inside `CoLine`)*
>> Reverses the transformation applied by `encode`, restoring the original grid arrangement.

> 🛡️ **`ParseShield`**
>> Utility class for hiding text by inserting invisible Unicode characters and decoding it back.

> 🛡️i **`encode(input_text, expansion_factor=5)`** *(Method inside `ParseShield`)*
>> Inserts random invisible characters after each character in the input, making the text visually unchanged (in console and some editors) but harder to parse.

> 🛡️i **`decode(input_text)`** *(Method inside `ParseShield`)*
>> Removes all invisible characters to restore the original text.

> **`Manage`**
>
>> Utility class for finding, launching, and managing processes across different operating systems.

> **`find(name)`** *(Method inside `Manage`)*
>
>> Searches for processes matching the given name.
>> Returns a tuple `(count, first_pid, other_pids)` with the number of matches, the first PID (if any), and a list of the remaining PIDs.

> **`launch(exe, args=None)`** *(Method inside `Manage`)*
>
>> Starts a new process by launching the given executable with optional arguments.
>> Returns the process ID of the launched process.

> **`terminate(pid)`** *(Method inside `Manage`)*
>
>> Attempts to gracefully terminate the process with the given PID.
>> Returns `True` if successful, `False` otherwise.

> **`kill_all(name)`** *(Method inside `Manage`)*
>
>> Terminates all processes with the given name.
>> Returns the number of processes successfully terminated.

> **`kill_others(name, keep_pid)`** *(Method inside `Manage`)*
>
>> Terminates all processes with the given name except for the one with `keep_pid`.
>> Returns the number of processes terminated.

> **`get_by_pid(pid)`** *(Method inside `Manage`)*
>
>> Retrieves information about a process by its PID.
>> Returns a dictionary containing `pid`, `name`, and `status` if found, or `None` if not running.

> **`get_pids_by_name(name)`** *(Method inside `Manage`)*
>
>> Retrieves a list of processes with the specified name.
>> Each entry is a dictionary containing `pid`, `name`, and `start_time`.

> **`who_launched_me()`**
>
>> Returns information about the process that launched the current script.
>> Provides a tuple `(pid, name)` of the launching process, or the last process in the tree if all parents are Python interpreters.
>> Returns `None` if no information is available.