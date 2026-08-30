**FoxyProxy** allows you to switch between proxies such as burp suite. This is useful when intercepting or routing traffic through different tools during an engagement.

**User-Agent Switcher and Manager** changes the User-Agent string to emulate different browsers, operating systems, or devices. You can present as mobile Safari or an older browser version to discover mobile-specific endpoints or version-specific behaviour. However, many modern WAFs and CDNs detect suspicious or rapid User-Agent changes.

**Wappalyzer** automatically identifies technologies used on the site, including platforms, web servers, JavaScript frameworks, analytics tools, CDNs, and databases. It runs passively while you browse and is one of the most widely used extensions for quick technology fingerprinting.

curl for HTTP banner --> `curl -I http://domain.com`


