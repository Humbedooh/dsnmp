
## HTML Generating template
html_temp_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
               "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml"> 
  <head> 
    <style type="text/css">
    body {
        font: 13px/1.5 Helvetica, Arial, 'Liberation Sans', FreeSans, sans-serif;
    }
     tr:nth-of-type(odd) td {
        background-color: #222;
     }
     tr:nth-of-type(even) td {
        background-color: #444;
     }
    
   table {
    border-collapse: separate;
    border-spacing: 0;
    min-width: 350px;
    box-shadow: 6px 6px 10px 3px rgba(0,0,0,0.75);
    border-radius: 6px;
    margin: 0px auto;
    text-align: left;
  }
  table tr th,
  table tr td {
      border-right: 1px solid #bbb;
      border-bottom: 1px solid #bbb;
      padding: 5px;
  }
  table tr th:first-child,
  table tr td:first-child {
      border-left: 1px solid #bbb;
  }
  table tr th:first-child,
  table tr td:first-child {
      border-left: 1px solid #bbb;
  }
  table.Info tr th,
  table.Info tr:first-child td
  {
      border-top: 1px solid #bbb;
  }

  table tr:first-child th:first-child,
  table.Info tr:first-child td:first-child {
      border-top-left-radius: 9px;
  }
  table tr:first-child th:last-child,
  table.Info tr:first-child td:last-child {
      border-top-right-radius: 9px;
  }
  table tr:last-child td:first-child {
      border-bottom-left-radius: 9px;
  }
  table a {
    color: #FF9;
    font-weight: bolder;
    text-decoration: none;
  }

  table tr:last-child td:last-child {
      border-bottom-right-radius: 9px;
      
  }
  table thead tr th {
        background: linear-gradient(to bottom, #7c8587 0%%,#3f4344 49%%,#5c6360 50%%,#0a0e0a 51%%,#0a0809 100%%);
        color: #6aF;
        text-align: center;
   }
   table tbody tr td {
      color: #FFF;
      
   }
   body {
    text-align: center;
   }
    div.loader_big {
            width:            64px;
            height:           64px;
            background-image: url(/loader.gif);
            margin: 0px auto;
    }
    div.loader_small {
            width:            24px;
            height:           24px;
            background-image: url(/loader.gif);
            margin: 0px auto;
    }

    </style>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>dSNMP Status Page</title>
  </head>
    <body>
        <p style="text-align: center;"><img src="/logo.png"/></p>
        <p>This page is currently being generated, hold on...<div class='loader_big'></div></p>
        <p><small><i>Powered by <a href="https://github.com/Humbedooh/dsnmp" rel="nofollow">dSNMP</a>.</i></small></p>
    </body>
</html>
"""

## HTML Output template
html_output_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
               "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml"> 
  <head> 
    <style type="text/css">
    body {
        font: 13px/1.5 Helvetica, Arial, 'Liberation Sans', FreeSans, sans-serif;
    }
     tr:nth-of-type(odd) td {
        background-color: #222;
     }
     tr:nth-of-type(even) td {
        background-color: #444;
     }
    
   table {
    border-collapse: separate;
    border-spacing: 0;
    min-width: 350px;
    box-shadow: 6px 6px 10px 3px rgba(0,0,0,0.75);
    border-radius: 6px;
    margin: 0px auto;
    text-align: left;
  }
  table tr th,
  table tr td {
      border-right: 1px solid #bbb;
      border-bottom: 1px solid #bbb;
      padding: 5px;
  }
  table tr th:first-child,
  table tr td:first-child {
      border-left: 1px solid #bbb;
  }
  table tr th:first-child,
  table tr td:first-child {
      border-left: 1px solid #bbb;
  }
  table.Info tr th,
  table.Info tr:first-child td
  {
      border-top: 1px solid #bbb;
  }

  table tr:first-child th:first-child,
  table.Info tr:first-child td:first-child {
      border-top-left-radius: 9px;
  }
  table tr:first-child th:last-child,
  table.Info tr:first-child td:last-child {
      border-top-right-radius: 9px;
  }
  table tr:last-child td:first-child {
      border-bottom-left-radius: 9px;
  }
  table a {
    color: #FF9;
    font-weight: bolder;
    text-decoration: none;
  }

  table tr:last-child td:last-child {
      border-bottom-right-radius: 9px;
      
  }
  table thead tr th {
        background: linear-gradient(to bottom, #7c8587 0%%,#3f4344 49%%,#5c6360 50%%,#0a0e0a 51%%,#0a0809 100%%);
        color: #6aF;
        text-align: center;
   }
   table tbody tr td {
      color: #FFF;
      
   }
   .checkbox_good {
        border: 1px solid #6A2;
        border-radius: 10px;
        background: linear-gradient(to bottom, #9dd53a 0%%,#a1d54f 50%%,#80c217 51%%,#7cbc0a 100%%);
        color: #FFF;
        font-weight: bold;
        padding-left: 4px;
        padding-right: 4px;
   }
   .checkbox_good:before {
    content: "\\2713"
   }
   .checkbox_bad {
        border: 1px solid #B52;
        border-radius: 10px;
        background: linear-gradient(to bottom, #f85032 0%%,#f16f5c 50%%,#f6290c 51%%,#f02f17 71%%,#e73827 100%%);
        color: #FFF;
        font-weight: bold;
        padding-left: 4px;
        padding-right: 4px;
        margin-right: 8px;
   }
   .checkbox_bad:before {
    content: "\\2717"
   }
   .bad {
    color: #E50; font-weight: bold;
   }
   body {
    text-align: center;
   }
    div.loader_big {
            width:            100px;
            height:           100px;
            background-image: url(/loader.gif);
    }
    div.loader_small {
            width:            100px;
            height:           100px;
            background-image: url(/loader.gif);
    }

    </style>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>dSNMP Status Page</title>
  </head>
    <body>
    <p style="text-align: center;"><img src="/logo.png"/></p>
        %s
        <table style="font-size: 11pt;">
          <thead>
            <tr>
              <th>Host</th>
              <th>Status</th>
              <th>Last checked</th>
            </tr>
          </thead>
          <tbody>
            %s
          </tbody>
        </table>
        <p><small><i>Powered by <a href="https://github.com/Humbedooh/dsnmp" rel="nofollow">dSNMP</a>.</i></small></p>
    </body>
</html>
"""

# Individual report template
html_report_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
               "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml"> 
  <head> 
    <style type="text/css">
    body {
        font: 13px/1.5 Helvetica, Arial, 'Liberation Sans', FreeSans, sans-serif;
    }
     tr:nth-of-type(odd) td {
        background-color: #222;
     }
     tr:nth-of-type(even) td {
        background-color: #444;
     }
    
   table {
    border-collapse: separate;
    border-spacing: 0;
    min-width: 350px;
    box-shadow: 6px 6px 10px 3px rgba(0,0,0,0.75);
    border-radius: 6px;
    margin: 0px auto;
    text-align: left;
  }
  table tr th,
  table tr td {
      border-right: 1px solid #bbb;
      border-bottom: 1px solid #bbb;
      padding: 5px;
  }
  table tr th:first-child,
  table tr td:first-child {
      border-left: 1px solid #bbb;
  }
  table tr th:first-child,
  table tr td:first-child {
      border-left: 1px solid #bbb;
  }
  table.Info tr th,
  table.Info tr:first-child td
  {
      border-top: 1px solid #bbb;
  }

  table tr:first-child th:first-child,
  table.Info tr:first-child td:first-child {
      border-top-left-radius: 9px;
  }
  table tr:first-child th:last-child,
  table.Info tr:first-child td:last-child {
      border-top-right-radius: 9px;
  }
  table tr:last-child td:first-child {
      border-bottom-left-radius: 9px;
  }
  table a {
    color: #FF9;
    font-weight: bolder;
    text-decoration: none;
  }

  table tr:last-child td:last-child {
      border-bottom-right-radius: 9px;
      
  }
  table thead tr th {
        background: linear-gradient(to bottom, #7c8587 0%%,#3f4344 49%%,#5c6360 50%%,#0a0e0a 51%%,#0a0809 100%%);
        color: #6aF;
        text-align: center;
   }
   table tbody tr td {
      color: #FFF;
      
   }
   body {
    text-align: center;
   }
    </style>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>dSNMP Status Page: %s</title>
  </head>
    <body>
    <p style="text-align: center;"><img src="/logo.png"/></p>
    <p><small><a href="./">Back to front page</a></small></p>
        %s
        <table style="font-size: 11pt;">
          <thead>
            <tr>
              <th>Check</th>
              <th>Response</th>
            </tr>
          </thead>
          <tbody>
            %s
          </tbody>
        </table>
        <p><small><i>Powered by <a href="https://github.com/Humbedooh/dsnmp" rel="nofollow">dSNMP</a>.</i></small></p>
    </body>
</html>
"""

favicon =  """AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAgAAAAMAAAADAAAAAgAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAALAAAAIQAAADsAAABFAAAAQQAAADgAAAArAAAAHAAAAA4AAAAFAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAADAAIANgUWBJgIHwa6BRcEuwIGAaUAAACCAAAAZAAAAE4AAAA2AAAAHAAAAAoAAAACAAAAAAAAAAAAAAAAAAAADA01Cq4mkB3/K6Yi/ymeIP8jhhv+GF0T7wopCMkBBQGRAAAAZQAAAEcAAAAkAAAACwAAAAEAAAAAAAAAAAAAABMVUhDLMr4n/yqfIf4XWBLwG2cV7SOHHPspnCD/HGwV9QYaBb4AAAB3AAAASwAAACAAAAAHAAAAAAAAAAAAAAAIEEEMszC2Jv8gexn8AAEApQAAAGADDQNrEkYOwyiZH/0ljR3+CSQHzAAAAHYAAAA+AAAAEgAAAAIAAAAAAAAAAAopCIsspiL/J5Yf/wQQA7AAAABHAAAAEgAAABoNNQqmKqEh/yOHG/0EEgO3AAAAWgAAACIAAAAGAAAAAwAAAAYEEANoJY4d/S2tJP8JJQfKAAAAWQAAAB4AAAABAAAAKRdbEtwxuSb/FE4P6gAAAHkAAAAuAAAACgAAAAcAAAAYAAAAXh1yF/Ixuyf/ED4M4AAAAGoAAAAmAAAABgAAAAkNNQqmLrAk/yF/GvsBBAGTAAAAMQAAAAsAAAAgBxwGmgIIAaEVUxDmMr4n/xhcEvAAAAB/AAAANAAAABUAAAAdCy4Iqi2tI/8mjh3/AgkCmAAAACoAAAAJAAIARRxuFvEZXxP0DjYK8TG7J/8gfRn7AAMAmwAAAFEAAAA+AAAAYhROD+Ayvif/IoQb+wEGAX0AAAAbAAAABQAAACcWVhHWLq4k/yOJG/8nlx7/GmQU/QEDAbAAAACCAQQBlw44C9kqoCH/Mrwn/xVSEOAAAABDAAAADAAAAAIAAAAABBEDUxdYEtwpnCD/KqMh/yB9Gf8XWxLxGF0T7iGAGvsuryT/L7El/xtrFe8FFQNyAAAAEAAAAAMAAAAAAAAAAAAAAAEAAwArCSUHhxVREM0dchfsIX4a+iKAG/wifxr5G2gV5w87DLoDDAJWAAAADAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAATAAAAMQABAEgAAgBMAAEARwAAAC0AAAAOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgB8AAIADAACAAQAAgAEAAIAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIABAADgAwAA//8AAA=="""

logo = """
iVBORw0KGgoAAAANSUhEUgAAAPAAAABhCAYAAAGfaBziAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyZpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMDE0IDc5LjE1Njc5NywgMjAxNC8wOC8yMC0wOTo1MzowMiAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTQgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjY1QTYyRkQ1OEU3RTExRTRBMkQ3QUYyMDgwNjVBNTIyIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjY1QTYyRkQ2OEU3RTExRTRBMkQ3QUYyMDgwNjVBNTIyIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6NjVBNjJGRDM4RTdFMTFFNEEyRDdBRjIwODA2NUE1MjIiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6NjVBNjJGRDQ4RTdFMTFFNEEyRDdBRjIwODA2NUE1MjIiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz7LbFpJAABG60lEQVR42sxU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"""

loader = """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"""
