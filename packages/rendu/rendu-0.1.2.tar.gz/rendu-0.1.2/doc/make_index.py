#!/bin/env python3
import os

here = os.path.dirname(os.path.realpath(__file__))

with open(f'{here}/pub_doc/index.html', 'w') as ofh:
    ofh.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rendu API Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem 1rem;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.05)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }

        .header h1 {
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 1;
        }

        .header h2 {
            font-size: 1.4rem;
            font-weight: 300;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        .content {
            padding: 3rem 2rem;
        }

        .version-list {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }

        .version-item {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .version-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
            transition: left 0.5s;
        }

        .version-item:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
        }

        .version-item:hover::before {
            left: 100%;
        }

        .version-number {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }

        .version-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .api-icon {
            width: 24px;
            height: 24px;
            display: inline-block;
            vertical-align: middle;
            margin-right: 0.5rem;
            fill: currentColor;
        }

        .footer {
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            padding: 2rem;
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.2rem;
            }
            
            .header h2 {
                font-size: 1.2rem;
            }
            
            .version-list {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .content {
                padding: 2rem 1rem;
            }
        }

    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>
                <svg class="api-icon" viewBox="0 0 24 24">
                    <path d="M14,17H7V15H14M17,13H7V11H17M17,9H7V7H17M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3Z"/>
                </svg>
                Rendu API Documentation
            </h1>
            <h2>Rendu Versions</h2>
        </header>
        
        <main class="content">
            <p style="text-align: center; color: #6c757d; margin-bottom: 1rem; font-size: 1.1rem;">
                Browse through all available versions of the Rendu API. Each version includes comprehensive documentation, examples, and migration guides.
            </p>
            
            <ul class="version-list">
""")
    with open(f'{here}/pub_doc/api_versions.txt', 'r') as ifh:
        versions = reversed(ifh.readlines())
        for i, version in enumerate(versions):
            ofh.write('<li class=" version-item">\n')
            ofh.write(f'    <div class=" version-number"><a href=./archive/rendu_{version}/index.html>rendu_{version}</a></div>\n')
            vtype = "Latest" if i == 0 else "Release"
            ofh.write(f'<span class="version-badge">{vtype}</span>\n')
            ofh.write('</li>\n')


    ofh.write("""
            </ul>
        </main>
        
        <footer class="footer">
            <p>
                Rendu API Documentation • Complete Reference API 
            </p>
        </footer>
    </div>
</body>
</html>
 """)
