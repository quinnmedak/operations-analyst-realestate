---
title: IIS 10.0 Detailed Error - 403.0 - Forbidden
url: https://assets.cushmanwakefield.com/-/media/cw/marketbeat-pdfs/2026/q2/us-reports/office/los-angeles_office_marketbeat-q2-2026.pdf
scraped_at: 2026-05-04T02:16:41
---

### HTTP Error 403.0 - Forbidden

#### You do not have permission to view this directory or page.

#### Most likely causes:

- This is a generic 403 error and means the authenticated user is not authorized to view the page.

#### Things you can try:

- Create a tracing rule to track failed requests for this HTTP status code. For more information about creating a tracing rule for failed requests, click [here](http://go.microsoft.com/fwlink/?LinkID=66439).

#### Detailed Error Information:

| Module | SitecoreHttpModuleExtensions |
| Notification | ExecuteRequestHandler |
| Handler | AutowiredPageHandlerFactory |
| Error Code | 0x00000000 |

| Requested URL | https://cw-prod-emeagws-a-cd\_\_6476:80/sitecore/service/notfound.aspx |
| Physical Path | C:\\home\\site\\wwwroot\\sitecore\\service\\notfound.aspx |
| Logon Method | Anonymous |
| Logon User | Anonymous |

#### More Information:


This generic 403 error means that the authenticated user is not authorized to use the requested resource. A substatus code in the IIS log files should indicate the reason for the 403 error. If a substatus code does not exist, use the steps above to gather more information about the source of the error.


[View more information »](https://go.microsoft.com/fwlink/?LinkID=62293&IIS70Error=403,0,0x00000000,20348)
