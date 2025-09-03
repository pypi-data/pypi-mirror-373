html_str = """
<!--https://heroicons.com/-->

<!DOCTYPE html>
<html lang="en">

<!--HTML Head-->
<head>
    <!-- Title -->
    <title>REPORT</title>
    <!-- Icon -->
    <link rel="icon" href="https://raw.githubusercontent.com/troymjose/test_rest_api/main/assets/test_rest_api.ico"
          type="image/x-icon">
    <!-- Tailwind CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- UTF-8 -->
    <meta charset="utf-8"/>
    <!-- Viewport -->
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
</head>

<!--HTML Body-->
<body class="bg-gray-50">

<!--Navbar-->
<nav id="navbar" class="fixed top-0 z-10 border-gray-700 bg-[#20283E] w-full bg-opacity-80">
    <div class="sm:px-10 px-5 grid sm:grid-cols-2 items-center mx-auto p-4 gap-4">
        <h1 class="flex items-center space-x-3 rtl:space-x-reverse">
            <!--Navbar Logo-->
            <!-- <img src="https://raw.githubusercontent.com/troymjose/test_rest_api/main/assets/test_rest_api.ico" class="h-8" alt=""/> -->
            <!--Navbar Title-->
            <span class="self-center text-3xl font-semibold whitespace-nowrap text-white">Test Rest Api</span>
        </h1>
        <!--Navbar Buttons-->
        <div class="flex sm:justify-end justify-start gap-3">
            <!--Test Dashboard-->
            <a class="group rounded-lg border hover:bg-white" href="#invisible-div-below-navbar">
                <svg class="min-w-6 min-h-6 text-white m-1 group-hover:mx-2 group-hover:bg-white group-hover:text-gray-900"
                     aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" />
                </svg>
            </a>
            <!--Test Execution Timeline-->
            <a class="group rounded-lg border hover:bg-white" href="#test-execution-timeline">
                <svg  class="min-w-6 min-h-6 text-white m-1 group-hover:mx-2 group-hover:bg-white group-hover:text-gray-900" 
                      aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" ill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941" />
                </svg>
            </a>
            <!--Tests-->
            <a class="group rounded-lg border hover:bg-white" href="#testcases">
                <svg class="min-w-6 min-h-6 text-white m-1 group-hover:mx-2 group-hover:bg-white group-hover:text-gray-900"
                     aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
                </svg>
            </a>
            <!--Info-->
            <a class="group rounded-lg border hover:bg-white" type="submit" href="https://pypi.org/project/test-rest-api/" target="_blank">
                <svg class="min-w-6 min-h-6 text-white m-1 group-hover:mx-2 group-hover:bg-white group-hover:text-gray-900"
                     aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
                </svg>
            </a>
        </div>
    </div>
</nav>

<!--Invisible Div below Navbar-->
<div id="invisible-div-below-navbar" class="min-h-[80px]"></div>

<!-- Dashboard - Summary -->
<div class="grid 2xl:grid-cols-12">
    <!--Dashboard - Summary First Column-->
    <div class="sm:col-span-3 flex flex-col justify-between gap-y-6 p-4 text-center">
        <!--Column Sub Container-->
        {% if summary.test.status %}
        <h5 class="text-8xl py-2 font-extrabold tracking-wide text-[#4bc0c0] drop-shadow-md bg-white rounded-md hover:drop-shadow-xl hover:tracking-wider">
            PASS</h5>
        {% else %}
        <h5 class="text-8xl py-2 font-extrabold tracking-wide text-[#ff6384] drop-shadow-md bg-white rounded-md hover:drop-shadow-xl hover:tracking-wider">
            FAIL</h5>
        {% endif %}
        <!--Column Sub Container-->
        <div class="group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Vertical Stepper-->
            <ol class="pl-12 space-y-8 overflow-hidden group-hover:pl-11">
                <!--Start Date Time-->
                <li class="relative flex-1 after:content-['']  after:w-0.5 after:h-full  after:bg-gray-200 after:inline-block after:absolute after:-bottom-11 after:left-4 lg:after:left-5">
                    <div class="flex items-center font-medium w-full">
                        <span class="w-8 h-8 bg-gray-50 border-2 border-gray-300 rounded-full flex justify-center
                                    items-center mr-3 text-sm text-white lg:w-10 lg:h-10">
                            <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.347a1.125 1.125 0 0 1 0 1.972l-11.54 6.347a1.125 1.125 0 0 1-1.667-.986V5.653Z" />
                            </svg>
                        </span>
                        <div class="block">
                            <h4 class="text-lg font-bold text-gray-600">Start date time</h4>
                            <span class="text-sm font-semibold text-gray-500 group-hover:font-extrabold">{{ summary.test.start }}</span>
                        </div>
                    </div>
                </li>
                <!--Duration-->
                <li class="relative flex-1 after:content-['']  after:w-0.5 after:h-full  after:bg-gray-200 after:inline-block after:absolute after:-bottom-12 after:left-4 lg:after:left-5">
                    <div class="flex items-center font-medium w-full">
                        <span class="w-8 h-8 bg-gray-50 border-2 border-gray-300 rounded-full flex justify-center items-center mr-3 text-sm text-indigo-600 lg:w-10 lg:h-10">
                            <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true"  xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                            </svg>
                        </span>
                        <div class="block">
                            <h4 class="pl-4 text-lg font-bold text-gray-600">Total duration</h4>
                            <span class="text-sm font-semibold text-gray-500 group-hover:font-extrabold">{{ summary.test.duration }}</span>
                        </div>
                    </div>
                </li>
                <!--End Date Time-->
                <li class="relative flex-1 ">
                    <div class="flex items-center font-medium w-full">
                        <span class="w-8 h-8 bg-gray-50 border-2 border-gray-300 rounded-full flex justify-center items-center mr-3 text-sm  lg:w-10 lg:h-10">
                            <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 7.5A2.25 2.25 0 0 1 7.5 5.25h9a2.25 2.25 0 0 1 2.25 2.25v9a2.25 2.25 0 0 1-2.25 2.25h-9a2.25 2.25 0 0 1-2.25-2.25v-9Z" />
                            </svg>
                        </span>
                        <div class="block">
                            <h4 class="text-lg font-bold text-gray-600">End date time</h4>
                            <span class="text-sm font-semibold text-gray-500 group-hover:font-extrabold">{{ summary.test.end }}</span>
                        </div>
                    </div>
                </li>
            </ol>
        </div>
        <!--Column Sub Container-->
        <div class="group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Dashboard Table-->
            <div class="grid grid-cols-2 gap-y-6 justify-center">
                <!--Total Tests-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
                    </svg>
                    Total Tests
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.total }}</p>
                <!--Bugs-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0 1 12 12.75Zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 0 1-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.208 1.44.125 2.104.52 4.136 1.153 6.06M12 12.75a2.25 2.25 0 0 0 2.248-2.354M12 12.75a2.25 2.25 0 0 1-2.248-2.354M12 8.25c.995 0 1.971-.08 2.922-.236.403-.066.74-.358.795-.762a3.778 3.778 0 0 0-.399-2.25M12 8.25c-.995 0-1.97-.08-2.922-.236-.402-.066-.74-.358-.795-.762a3.734 3.734 0 0 1 .4-2.253M12 8.25a2.25 2.25 0 0 0-2.248 2.146M12 8.25a2.25 2.25 0 0 1 2.248 2.146M8.683 5a6.032 6.032 0 0 1-1.155-1.002c.07-.63.27-1.222.574-1.747m.581 2.749A3.75 3.75 0 0 1 15.318 5m0 0c.427-.283.815-.62 1.155-.999a4.471 4.471 0 0 0-.575-1.752M4.921 6a24.048 24.048 0 0 0-.392 3.314c1.668.546 3.416.914 5.223 1.082M19.08 6c.205 1.08.337 2.187.392 3.314a23.882 23.882 0 0 1-5.223 1.082" />
                    </svg>
                    Bugs
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.bugs.total }}</p>
                <!--Errors-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                    </svg>
                    Errors
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.errors.total }}</p>
                <!--Assertions-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0 0 12 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52 2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 0 1-2.031.352 5.988 5.988 0 0 1-2.031-.352c-.483-.174-.711-.703-.59-1.202L18.75 4.971Zm-16.5.52c.99-.203 1.99-.377 3-.52m0 0 2.62 10.726c.122.499-.106 1.028-.589 1.202a5.989 5.989 0 0 1-2.031.352 5.989 5.989 0 0 1-2.031-.352c-.483-.174-.711-.703-.59-1.202L5.25 4.971Z" />
                    </svg>
                    Assertions
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.assertions }}</p>
                <!--Test Logs-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                    </svg>
                    Test Logs
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.logs }}</p>
            </div>
        </div>
    </div>
    <!--Dashboard - Summary Second Column-->
    <div class="sm:col-span-3 flex flex-col justify-between gap-y-6 p-4 text-center">
        <!--Column Sub Container-->
        <div class="group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Sync Async Doughnut Chart-->
            <div class="p-6 min-h-[388px] group-hover:scale-105">
                <canvas id="syncAsyncDoughnutChart"></canvas>
            </div>
            <!--Dashboard Table-->
            <div class="grid grid-cols-2 gap-y-6 justify-center">
                <!--Sync-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8.242 5.992h12m-12 6.003H20.24m-12 5.999h12M4.117 7.495v-3.75H2.99m1.125 3.75H2.99m1.125 0H5.24m-1.92 2.577a1.125 1.125 0 1 1 1.591 1.59l-1.83 1.83h2.16M2.99 15.745h1.125a1.125 1.125 0 0 1 0 2.25H3.74m0-.002h.375a1.125 1.125 0 0 1 0 2.25H2.99" />
                    </svg>
                    Sync
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.sync_tests }}</p>
                <!--Async-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0ZM3.75 12h.007v.008H3.75V12Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm-.375 5.25h.007v.008H3.75v-.008Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
                    </svg>
                    Async
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.async_tests }}</p>
            </div>
        </div>
        <!--Column Sub Container-->
        <div class="group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl flex-grow">
            <div class="grid grid-cols-1 gap-y-6 justify-center">
                <div class="flex gap-x-3 font-bold text-gray-600 truncate group-hover:pl-1">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 8.25h15m-16.5 7.5h15m-1.8-13.5-3.9 19.5m-2.1-19.5-3.9 19.5" />
                    </svg>
                    Hash Tags
                </div>
                <article class="text-wrap text-left">
                    <p class="text-xs line-clamp-4 font-semibold text-gray-500 group-hover:font-extrabold pl-1 group-hover:pl-2">
                        {{ '#' + ' #'.join(summary.test.tags) if summary.test.tags else '#ALL' }}
                    </p>
                </article>
            </div>

        </div>
    </div>
    <!--Dashboard - Summary Third Column-->
    <div class="sm:col-span-3 flex flex-col justify-between gap-y-6 p-4 text-center">
        <!--Column Sub Container-->
        <div class="group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Request Response Doughnut Chart-->
            <div class="p-6 min-h-[388px] group-hover:scale-105">
                <canvas id="reqRespDoughnutChart"></canvas>
            </div>
            <!--Dashboard Table-->
            <div class="grid grid-cols-2 gap-y-6 justify-center">
                <!--Requests-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                    </svg>
                    Requests
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.requests }}</p>
                <!--Responses-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 9.75v6.75m0 0-3-3m3 3 3-3m-8.25 6a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                    </svg>
                    Responses
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.responses }}</p>
            </div>
        </div>
        <!--Column Sub Container-->
        <div class="group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Dashboard Table-->
            <div class="grid grid-cols-2 gap-y-6 justify-center">
                <!--Environments-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
                    </svg>
                    Environments
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.environment_variables }}</p>
                <!--Testdata-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 6.878V6a2.25 2.25 0 0 1 2.25-2.25h7.5A2.25 2.25 0 0 1 18 6v.878m-12 0c.235-.083.487-.128.75-.128h10.5c.263 0 .515.045.75.128m-12 0A2.25 2.25 0 0 0 4.5 9v.878m13.5-3A2.25 2.25 0 0 1 19.5 9v.878m0 0a2.246 2.246 0 0 0-.75-.128H5.25c-.263 0-.515.045-.75.128m15 0A2.25 2.25 0 0 1 21 12v6a2.25 2.25 0 0 1-2.25 2.25H5.25A2.25 2.25 0 0 1 3 18v-6c0-.98.626-1.813 1.5-2.122" />
                    </svg>
                    Testdata
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.testdata_variables }}</p>
                <!--Testdata Files-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6.429 9.75 2.25 12l4.179 2.25m0-4.5 5.571 3 5.571-3m-11.142 0L2.25 7.5 12 2.25l9.75 5.25-4.179 2.25m0 0L21.75 12l-4.179 2.25m0 0 4.179 2.25L12 21.75 2.25 16.5l4.179-2.25m11.142 0-5.571 3-5.571-3" />
                    </svg>
                    Testdata Files
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.test.testdata_files }}</p>
            </div>
        </div>
    </div>
    <!--Dashboard - Summary Fourth Column-->
    <div class="sm:col-span-3 flex flex-col justify-between gap-y-6 p-4 text-center">
        <!--Column Sub Container-->
        <div class="group py-6 px-3 flex-grow bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Testcase Status Doughnut Chart-->
            <div class="p-6 min-h-[388px] group-hover:scale-105">
                <canvas id="statusDoughnutChart"></canvas>
            </div>
            <!--Dashboard Table-->
            <div class="grid grid-cols-2 gap-y-6 justify-center">
                <!--Total-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" />
                    </svg>
                    Total
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.total }}</p>
                <!--Pass-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                    Pass
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.success }}</p>
                <!--Fail-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 12.75c1.148 0 2.278.08 3.383.237 1.037.146 1.866.966 1.866 2.013 0 3.728-2.35 6.75-5.25 6.75S6.75 18.728 6.75 15c0-1.046.83-1.867 1.866-2.013A24.204 24.204 0 0 1 12 12.75Zm0 0c2.883 0 5.647.508 8.207 1.44a23.91 23.91 0 0 1-1.152 6.06M12 12.75c-2.883 0-5.647.508-8.208 1.44.125 2.104.52 4.136 1.153 6.06M12 12.75a2.25 2.25 0 0 0 2.248-2.354M12 12.75a2.25 2.25 0 0 1-2.248-2.354M12 8.25c.995 0 1.971-.08 2.922-.236.403-.066.74-.358.795-.762a3.778 3.778 0 0 0-.399-2.25M12 8.25c-.995 0-1.97-.08-2.922-.236-.402-.066-.74-.358-.795-.762a3.734 3.734 0 0 1 .4-2.253M12 8.25a2.25 2.25 0 0 0-2.248 2.146M12 8.25a2.25 2.25 0 0 1 2.248 2.146M8.683 5a6.032 6.032 0 0 1-1.155-1.002c.07-.63.27-1.222.574-1.747m.581 2.749A3.75 3.75 0 0 1 15.318 5m0 0c.427-.283.815-.62 1.155-.999a4.471 4.471 0 0 0-.575-1.752M4.921 6a24.048 24.048 0 0 0-.392 3.314c1.668.546 3.416.914 5.223 1.082M19.08 6c.205 1.08.337 2.187.392 3.314a23.882 23.882 0 0 1-5.223 1.082" />
                    </svg>
                    Fail
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.fail }}</p>
                <!--Error-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                    </svg>
                    Error
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.error }}</p>
                <!--Disable-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                    Disable
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.disable }}</p>
                <!--Skip-->
                <div class="flex gap-x-3 pl-12 font-bold text-gray-600 truncate group-hover:pl-11">
                    <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                    Skip
                </div>
                <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-1">{{ summary.tests.skip }}</p>
            </div>
        </div>
    </div>
</div>

<!--Dashboard - Bug and Error-->
<div class="grid 2xl:grid-cols-12">
    <!--Dashboard - Bug and Error First Column-->
    <div class="sm:col-span-6 flex flex-col justify-between gap-y-6 p-4 text-center">
        <div class="grid 2xl:grid-cols-12 group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Column Sub Container-->
            <div class="sm:col-span-6 flex flex-col justify-center gap-y-6 p-4 text-center">
                <div class="flex flex-col">
                    <h1 class="text-6xl mb-10 py-4 font-extrabold tracking-wide text-[#20283E] border border-gray-300 drop-shadow rounded-md group-hover:tracking-wider">
                        Bugs</h1>
                    <!--Dashboard Table-->
                    <div class="grid grid-cols-2 gap-y-6 justify-center">
                        <!--Total Tests-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">TOTAL</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.bugs.total }}</p>
                        <!--Bugs-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">LOW</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.bugs.low }}</p>
                        <!--Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">MINOR</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.bugs.minor }}</p>
                        <!--Assertions-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">MAJOR</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.bugs.major }}</p>
                        <!--Test Logs-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">CRITICAL</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.bugs.critical }}</p>
                        <!--Test Logs-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">BLOCKER</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.bugs.blocker }}</p>
                    </div>
                </div>

            </div>
            <!--Column Sub Container-->
            <div class="sm:col-span-6 flex flex-col justify-between gap-y-6 p-4 text-center">
                <div class="p-6 min-h-[384px] max-h-[384px] group-hover:scale-105">
                    <canvas id="bugDoughnutChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    <!--Dashboard - Bug and Error Second Column-->
    <div class="sm:col-span-6 flex flex-col justify-between gap-y-6 p-4 text-center">
        <div class="grid 2xl:grid-cols-12 group py-6 px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <!--Column Sub Container-->
            <div class="sm:col-span-6 flex flex-col justify-center gap-y-6 p-4 text-center">
                <div class="flex flex-col">
                    <h1 class="text-6xl mb-10 py-4 font-extrabold tracking-wide text-[#20283E] border border-gray-300 drop-shadow rounded-md group-hover:tracking-wider">
                        Errors</h1>
                    <!--Dashboard Table-->
                    <div class="grid grid-cols-2 gap-y-6 justify-center max-h-[264px] overflow-y-auto scroll-smooth">
                        <!--Total Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">TOTAL</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.total }}</p>
                        <!--Rest Api Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">REST API</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.rest_api }}</p>
                        <!--Assertion Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">ASSERTION</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.assertion }}</p>
                        <!--Unexpected Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">UNEXPECTED</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.unexpected }}</p>
                        <!--Bug Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">BUG</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.bug }}</p>
                        <!--Variable Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">VARIABLE</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.variable }}</p>
                        <!--Constant Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">CONSTANT</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.constant }}</p>
                        <!--Environment Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">ENVIRONMENT</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.environment }}</p>
                        <!--Test Data Errors-->
                        <p class="pl-12 font-bold text-left text-gray-600 truncate group-hover:pl-14">TEST DATA</p>
                        <p class="font-semibold text-gray-500 group-hover:font-extrabold group-hover:pl-2">{{ summary.errors.test_data }}</p>
                    </div>
                </div>

            </div>
            <!--Column Sub Container-->
            <div class="sm:col-span-6 flex flex-col justify-between gap-y-6 p-4 text-center">
                <div class="p-6 min-h-[384px] max-h-[384px] group-hover:scale-105">
                    <canvas id="errorDoughnutChart"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>

<!--Test Execution Timeline-->
<div  id="test-execution-timeline">
    <div class="sm:col-span-6 flex flex-col justify-between gap-y-6 p-4 text-center">
        <div class="group px-3 bg-white drop-shadow-md rounded-md hover:drop-shadow-xl">
            <div class="inline-flex items-center justify-center h-[180px] w-full">
                <hr class="w-11/12 h-px my-8 bg-gray-200 border">
                <span class="absolute px-4 font-medium text-gray-900 -translate-x-1/2 bg-white left-1/2">
                    <p class="text-6xl py-8 font-extrabold tracking-wider text-[#20283E] group-hover:tracking-widest">Test Execution Timeline</p>
                </span>
            </div>
            <div class="px-32 pb-20 group-hover:scale-105">
                <canvas id="timelineScatterChart"></canvas>
            </div>
        </div>
    </div>
</div>

<!--Testcases-->
<div id="testcases" class="p-4">
    <div class="flex flex-col bg-white drop-shadow-md rounded-md">
        <div class="group inline-flex items-center justify-center h-[180px] w-full">
            <hr class="w-11/12 h-px my-8 bg-gray-200 border">
            <span class="absolute px-6 font-medium text-gray-900 -translate-x-1/2 bg-white left-1/2">
                <p class="text-6xl py-10 font-extrabold tracking-wider text-[#20283E] group-hover:tracking-widest"> Tests</p>
            </span>
        </div>
        <!--Testcases-->
        <div class="flex flex-col gap-y-5">
            {% for test in tests.values() %}
            <button onclick="openTestcase('{{ test.name }}')"
                    class="group mx-8 p-4 flex justify-center bg-white rounded-md hover:drop-shadow-md border">
                <div class="grid justify-between gap-4 w-full 2xl:grid-cols-2">
                    <div class="flex gap-5">
                        {% if test.status == "pass" %}
                        <p class="min-w-[80px] max-w-[80px] group-hover:drop-shadow-md py-2 px-2 self-center font-extrabold border border-gray-300 drop-shadow rounded-md text-[#4bc0c0] bg-white text-center sm:text-base text-sm">PASS</p>
                        {% elif test.status == "fail" %}
                        <p class="min-w-[80px] max-w-[80px] group-hover:drop-shadow-md py-2 px-2 self-center font-extrabold border border-gray-300 drop-shadow rounded-md text-[#ff6384] bg-white text-center sm:text-base text-sm">FAIL</p>
                        {% elif test.status == "error" %}
                        <p class="min-w-[80px] max-w-[80px] group-hover:drop-shadow-md py-2 px-2 self-center font-extrabold border border-gray-300 drop-shadow rounded-md text-[#ffcd56] bg-white text-center sm:text-base text-sm">ERROR</p>
                        {% else %}
                        <p class="min-w-[80px] max-w-[80px] group-hover:drop-shadow-md py-2 px-2 self-center font-extrabold border border-gray-300 drop-shadow rounded-md text-[#ffcd56] bg-white text-center sm:text-base text-sm">ERROR</p>
                        {% endif %}
                        <div class="flex flex-col self-center">
                            <h1 class="font-semibold text-gray-600 line-clamp-1 group-hover:py-1 sm:text-xl test-xs group-hover:font-bold">
                                {{ test.name }}</h1>
                        </div>
                    </div>
                    <div class="flex justify-end gap-4 group-hover:gap-5">
                        <div class="w-20 py-2 self-center flex justify-center rounded-full bg-white drop-shadow sm:flex hidden">
                            <div class="flex gap-x-2 font-semibold text-gray-500">
                                <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0 0 12 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52 2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 0 1-2.031.352 5.988 5.988 0 0 1-2.031-.352c-.483-.174-.711-.703-.59-1.202L18.75 4.971Zm-16.5.52c.99-.203 1.99-.377 3-.52m0 0 2.62 10.726c.122.499-.106 1.028-.589 1.202a5.989 5.989 0 0 1-2.031.352 5.989 5.989 0 0 1-2.031-.352c-.483-.174-.711-.703-.59-1.202L5.25 4.971Z" />
                                </svg>
                                {{ test.counts.assertions }}
                            </div>
                        </div>
                        <div class="w-20 py-2 self-center flex justify-center drop-shadow bg-white rounded-full sm:flex hidden">
                            <div class="flex gap-x-2 font-semibold text-gray-500">
                                <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                                </svg>
                                {{ test.logs|length }}
                            </div>
                        </div>
                        <div class="w-20 py-2 self-center flex justify-center drop-shadow bg-white rounded-full sm:flex hidden">
                            <div class="flex gap-x-2 font-semibold text-gray-500">
                                <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                                </svg>
                                {{ test.counts.requests }}
                            </div>
                        </div>
                        <div class="w-20 py-2 self-center flex justify-center drop-shadow bg-white rounded-full sm:flex hidden">
                            <div class="flex gap-x-2 font-semibold text-gray-500">
                                <svg class="min-w-6 min-h-6 text-gray-700" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9.75v6.75m0 0-3-3m3 3 3-3m-8.25 6a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
                                </svg>
                                {{ test.counts.responses }}
                            </div>
                        </div>
                        <div class="w-20 py-2 self-center flex justify-center drop-shadow bg-white rounded-full sm:drop-shadow-none sm:text-base text-xs group-hover:tracking-widest">
                            {% if test.is_async %}
                            <div class="flex font-bold text-gray-600">ASYNC</div>
                            {% else %}
                            <div class="flex font-bold text-gray-600">SYNC</div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </button>
            {% endfor %}
        </div>
        <br>
    </div>
</div>
<br>

<!--Testcase Modal Overlay-->
<div id="testcase"
     onclick="closeTestcase()"
     class="flex justify-center items-center fixed left-0 right-0 top-0 bottom-0 bg-gray-600 bg-opacity-50 w-screen h-screen opacity-0 hidden transition-opacity duration-500">
    <!--Modal-->
    <div id="testcase-modal"
         class="flex flex-col bg-white drop-shadow-md rounded-md w-[95%] max-h-[90%] overflow-y-auto overscroll-contain scroll-smooth"
         onclick="event.stopImmediatePropagation()">
        <!--Inner White Bg Shadow Box-->
        <div class="mx-4">
            <div class="h-30 flex justify-between items-center gap-x-4 sticky top-0 p-4 z-50 bg-white text-gray-600">
                <p id="testcase-modal-testcase-status"
                    class="py-2 px-4 text-5xl font-bold rounded-2xl border-2"></p>
                <p id="testcase-modal-testcase-name"
                   class="text-xl font-semibold text-gray-600 tracking-widest pb-1 text-pretty"></p>
                <button onclick="closeTestcase()">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2"
                         stroke="currentColor" class="size-12">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>

            <div class="text-left py-6 px-3 bg-white">
                <ul class="flex flex-col divide-y divide-gray-200">
                    <li class="inline-flex flex-col gap-2 px-4 py-2 group-hover">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Testcase Description</h1>
                            <p id="testcase-modal-testcase-desc"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600 text-pretty"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Asynchronous</h1>
                            <p id="testcase-modal-testcase-is-async"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Testsuite</h1>
                            <p id="testcase-modal-testcase-testsuite"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Test Tags</h1>
                            <p id="testcase-modal-testcase-tags"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Start Date Time</h1>
                            <p id="testcase-modal-testcase-start"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                End Date Time</h1>
                            <p id="testcase-modal-testcase-end"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Test Duration</h1>
                            <p id="testcase-modal-testcase-duration"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Total Assertions</h1>
                            <p id="testcase-modal-testcase-counts-assertions"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Total Logs</h1>
                            <p id="testcase-modal-testcase-counts-logs"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>
                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Total Requests</h1>
                            <p id="testcase-modal-testcase-counts-requests"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Total Responses</h1>
                            <p id="testcase-modal-testcase-counts-responses"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600"></p>
                        </div>

                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <div class="group">
                            <h1 class="font-base text-gray-500 pt-1 sm:text-base text-xs">
                                Testcase Details</h1>
                            <pre id="testcase-modal-testcase-details"
                               class="font-semibold text-gray-500 tracking-widest pb-1 sm:text-lg text-xs group-hover:text-gray-600 text-pretty"></pre>
                        </div>
                    </li>
                    <li class="inline-flex flex-col gap-2 px-4 py-2">
                        <h1 class="font-base text-gray-500 py-1 sm:text-base text-xs">
                            Testcase Logs</h1>
                        <ol id="testcase-modal-testcase-logs" class="relative border-s border-gray-300"> </ol>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>

<!-- Chart.js cdn -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- luxon.js cdn -->
<script src="https://cdn.jsdelivr.net/npm/luxon@3.4.4/build/global/luxon.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.3.1/dist/chartjs-adapter-luxon.umd.js"></script>
<!-- Summary Status Doughnut Chart -->
<script>
    const statusDoughnutChart = document.getElementById(
      "statusDoughnutChart"
    );
    new Chart(statusDoughnutChart, {
      type: "doughnut",
      data: {
        labels: ["Pass", "Fail", "Error", "Disable", "Skip"],
        datasets: [
          {
            label: "Test Count",
            data: [{{ summary.tests.success }}, {{ summary.tests.fail }}, {{ summary.tests.error }}, {{ summary.tests.disable }}, {{ summary.tests.skip }}],
            backgroundColor: [
              "rgba(75, 192, 192,0.7)",
              "rgba(255, 99, 132, 0.7)",
              "rgba(255, 205, 86, 0.7)",
              "rgba(234, 106, 71, 0.7)",
              "rgba(28, 78, 128, 0.7)",
            ],
            hoverOffset: 4,
          },
        ],
      },
    });
</script>
<!-- Sync Async Bar Chart -->
<script>
    const syncAsyncDoughnutChart = document.getElementById(
      "syncAsyncDoughnutChart"
    );
    new Chart(syncAsyncDoughnutChart, {
      type: "doughnut",
      data: {
        labels: ["Synchronous Test", "Asynchronous Test"],
        datasets: [
          {
            label: "Test Count",
            data: [{{ summary.tests.sync_tests }}, {{ summary.tests.async_tests }}],
            backgroundColor: [
              "rgba(28, 78, 128, 0.7)",
              "rgba(0, 145, 213, 0.7)",
            ],
            hoverOffset: 4,
          },
        ],
      },
    });
</script>
<!-- Request Response Doughnut Chart -->
<script>
    const reqRespDoughnutChart = document.getElementById(
      "reqRespDoughnutChart"
    );
    new Chart(reqRespDoughnutChart, {
      type: "doughnut",
      data: {
        labels: ["Requests", "Responses"],
        datasets: [
          {
            label: "Count",
            data: [{{ summary.test.requests }}, {{ summary.test.responses }}],
            backgroundColor: [
              "rgba(75, 73, 172, 0.7)",
              "rgba(152, 189, 255, 0.7)",
            ],
            hoverOffset: 4,
          },
        ],
      },
    });
</script>
<!-- Summary Bug Doughnut Chart -->
<script>
    const bugDoughnutChart = document.getElementById("bugDoughnutChart");
    new Chart(bugDoughnutChart, {
      type: "doughnut",
      data: {
        labels: ["Low", "Minor", "Major", "Critical", "Blocker"],
        datasets: [
          {
            label: "Priority",
            data: [{{ summary.bugs.low }}, {{ summary.bugs.minor }}, {{ summary.bugs.major }}, {{ summary.bugs.critical }}, {{ summary.bugs.blocker }}],
            backgroundColor: [
              "rgba(126, 176, 213, 0.7)",
              "rgba(253, 57, 149, 0.7)",
              "rgba(253, 127, 111, 0.7)",
              "rgba(255, 181, 90, 0.7)",
              "rgba(194, 55, 40, 0.7)",
            ],
            hoverOffset: 4,
          },
        ],
      },
    });
</script>
<!-- Summary Error Doughnut Chart -->
<script>
    const errorDoughnutChart = document.getElementById("errorDoughnutChart");
    new Chart(errorDoughnutChart, {
      type: "doughnut",
      data: {
        labels: ["Rest Api", "Assertion", "Unexpected", "Bug", "Variable", "Constant", "Environment", "Test Data"],
        datasets: [
          {
            label: "Type",
            data: [{{ summary.errors.rest_api }}, {{ summary.errors.assertion }}, {{ summary.errors.unexpected }}, {{ summary.errors.bug }}, {{ summary.errors.variable }}, {{ summary.errors.constant }}, {{ summary.errors.environment }}, {{ summary.errors.test_data }}],
            backgroundColor: [
              "rgba(87, 68, 118, 0.5)",
              "rgba(29, 201, 183, 0.5)",
              "rgba(253, 57, 149, 0.5)",
              "rgba(57, 161, 244, 0.5)",
              "rgba(245, 166, 35, 0.5)",
              "rgba(37, 71, 106, 0.5)",
              "rgba(159, 204, 46, 0.5)",
              "rgba(220, 53, 69, 0.5)"
            ],
            hoverOffset: 4,
          },
        ],
      },
    });
</script>
<!-- Timeline (Gantt-style) Scatter Chart -->
<script>
const concurrency_data = {{ tests.values() | list | tojson | safe }}

// Date format
const fmt = "yyyy-MM-dd HH-mm-ss";

// Expand each test into many points so tooltip works anywhere along the line
function expandPoints(startStr, endStr, y, nPoints = 14) {
    const start = luxon.DateTime.fromFormat(startStr, fmt).toMillis();
    const end = luxon.DateTime.fromFormat(endStr, fmt).toMillis();
    if (!isFinite(start) || !isFinite(end) || end <= start) {
        return [];
    }
    const step = (end - start) / (nPoints - 1);
    const pts = [];
    for (let i = 0; i < nPoints; i++) {
        pts.push({x: start + i * step, y: y});
    }
    return pts;
}

// One dataset per test
const datasets = concurrency_data.map((t, idx) => ({
    label: `${t.name}`,
    data: expandPoints(t.start, t.end, t.name, 20),
    borderColor: `hsl(${(idx * 57) % 360}, 70%, 45%)`,
    backgroundColor: `hsl(${(idx * 57) % 360}, 70%, 45%)`,
    borderWidth: 6,
    showLine: true,
    pointRadius: 0,
    pointHitRadius: 10,
}));

const timelineScatterChart = document.getElementById("timelineScatterChart").getContext("2d");

new Chart(timelineScatterChart, {
    type: "scatter",
    data: {datasets},
    options: {
        indexAxis: "y",
        responsive: true,
        interaction: {mode: "nearest", intersect: false},
        plugins: {
            legend: {display: false},
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const test = concurrency_data[context.datasetIndex];
                        return [
                            `Test: ${test.name}`,
                            `Start: ${test.start}`,
                            `End: ${test.end}`,
                            `Duration: ${test.duration}s`,
                        ];
                    },
                },
            },
        },
        scales: {
            x: {
                type: "time",
                time: {
                    parser: fmt,
                    tooltipFormat: "yyyy-MM-dd HH:mm:ss",
                    displayFormats: {
                        minute: "HH:mm",
                        hour: "HH:mm",
                        second: "HH:mm:ss"

                    },
                },
                ticks: {
                    callback: (val) => luxon.DateTime.fromMillis(val).toFormat("HH:mm:ss"),
                },
                title: {display: true, text: "Time"},
            },
            y: {
                type: "category",
                labels: concurrency_data.map((t) => t.name),
                offset: true,
                reverse: true,
                title: {display: true, text: "Tests"},
            },
        },
        elements: {
            point: {hitRadius: 10},
        },
    },
});
</script>

<script>
    const tests = {{tests | tojson | safe}}

    function setTestcaseModel(testcase) {

        <!--Set Testcase Status-->
        const testcaseStatus = document.getElementById("testcase-modal-testcase-status");
        testcaseStatus.innerHTML = testcase.status.toUpperCase();
        <!--Set Testcase Status Color-->
        if (testcase.status.toUpperCase() === "PASS") {
            testcaseStatus.classList.add("text-[#4bc0c0]");
            testcaseStatus.classList.add("border-[#4bc0c0]");
            testcaseStatus.classList.remove("text-[#ff6384]");
            testcaseStatus.classList.remove("border-[#ff6384]");
        } else {
            testcaseStatus.classList.add("text-[#ff6384]");
            testcaseStatus.classList.add("border-[#ff6384]");
            testcaseStatus.classList.remove("text-[#4bc0c0]");
            testcaseStatus.classList.remove("border-[#4bc0c0]");
        }

        <!--Set Testcase Name-->
        const testcaseName = document.getElementById("testcase-modal-testcase-name");
        testcaseName.innerHTML = testcase.name;

        <!--Set Testcase Description-->
        const testcaseDescription = document.getElementById("testcase-modal-testcase-desc");
        testcaseDescription.innerHTML = testcase.desc;

        <!--Set Testcase Is Async-->
        const testcaseIsAsync = document.getElementById("testcase-modal-testcase-is-async");
        testcaseIsAsync.innerHTML = testcase.is_async ? "Yes" : "No";

        <!--Set Testcase Testsuite-->
        const testcaseTestsuite = document.getElementById("testcase-modal-testcase-testsuite");
        testcaseTestsuite.innerHTML = testcase.testsuite;

        <!--Set Testcase Tags-->
        const testcaseTags = document.getElementById("testcase-modal-testcase-tags");
        testcaseTags.innerHTML = testcase.tags ? testcase.tags : "No tags provided";

        <!--Set Testcase Start Date Time-->
        const testcaseStart = document.getElementById("testcase-modal-testcase-start");
        testcaseStart.innerHTML = testcase.start;

        <!--Set Testcase End Date Time-->
        const testcaseEnd = document.getElementById("testcase-modal-testcase-end");
        testcaseEnd.innerHTML = testcase.end;

        <!--Set Testcase Duration-->
        const testcaseDuration = document.getElementById("testcase-modal-testcase-duration");
        testcaseDuration.innerHTML = testcase.duration;

        <!--Set Testcase Assertions-->
        const testcaseAssertions = document.getElementById("testcase-modal-testcase-counts-assertions");
        testcaseAssertions.innerHTML = testcase.counts.assertions;

        <!--Set Testcase Logs-->
        const testcaseCountsLogs = document.getElementById("testcase-modal-testcase-counts-logs");
        testcaseCountsLogs.innerHTML = testcase.logs.length;

        <!--Set Testcase Requests-->
        const testcaseCountsRequests = document.getElementById("testcase-modal-testcase-counts-requests");
        testcaseCountsRequests.innerHTML = testcase.counts.requests;

        <!--Set Testcase Responses-->
        const testcaseCountsResponses = document.getElementById("testcase-modal-testcase-counts-responses");
        testcaseCountsResponses.innerHTML = testcase.counts.responses;
        
        <!--Set Testcase Details-->
        const testcaseDetails = document.getElementById("testcase-modal-testcase-details");
        testcaseDetails.innerHTML = testcase.details;

        <!--Set Testcase Logs-->
        const testcaseLogs = document.getElementById("testcase-modal-testcase-logs");

        <!--Create the unordered list element and set its inner HTML using map() and join()-->
        let ul = `<ul>${testcase.logs.map(log =>
         `<li class="mb-10 ms-4">
         <div class="group">
         <div class="absolute w-3 h-3 bg-gray-400 rounded-full mt-1.5 -start-1.5 border border-white group-hover:bg-gray-600"></div>
         <p class=" italic pt-0.5 text-sm font-normal text-gray-500 tracking-wider group-hover:tracking-widest group-hover:text-gray-600">${log.datetime}</p>
         <div class="flex items-center gap-1">
         <h3 class="text-lg font-semibold text-gray-500 tracking-wider group-hover:tracking-widest group-hover:text-gray-600">${log.level}</h3>
         <p class="text-xs font-light text-gray-500 tracking-wider group-hover:tracking-widest group-hover:text-gray-600">${log.internal ? "internal" : "custom"}</p>
         </div>
         <pre class="mb-4 text-base font-normal text-gray-500 group-hover:text-gray-600 group-hover:pl-1">${log.message}</pre>
         </div></li>`).join('')}</ul>`;

         // Set the inner HTML of the testcaseLogs element
         testcaseLogs.innerHTML = ul;

    }
</script>

<!--show testcase-->
<script>

    function openTestcase(testcaseName) {

        <!--Set Testcase Model-->
        setTestcaseModel(tests[testcaseName]);

        const testcase = document.getElementById("testcase");
        testcase.classList.toggle("hidden");
        testcase.classList.toggle("opacity-0");

        const testcaseModel = document.getElementById("testcase-modal");
        testcaseModel.scrollTo(0,0);

        const body = document.body;
        body.classList.add('overflow-hidden');

        const navbar = document.getElementById("navbar");
        navbar.classList.add('hidden');
    }

    function closeTestcase() {

        currentTestcaseName = "";

        const testcase = document.getElementById("testcase");
        testcase.classList.toggle("hidden");
        testcase.classList.toggle("opacity-0");

        const body = document.body;
        body.classList.remove('overflow-hidden');

        const navbar = document.getElementById("navbar");
        navbar.classList.remove('hidden');
    }
</script>



</body>

</html>
"""
