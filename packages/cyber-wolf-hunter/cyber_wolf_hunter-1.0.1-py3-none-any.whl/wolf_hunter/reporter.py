"""
HTML Report generation for vulnerability scan results
"""

import os
import json
from datetime import datetime
from jinja2 import Template


class HTMLReporter:
    """
    Generate professional HTML reports for vulnerability scan results
    """
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    
    def generate_html_report(self, results, filename="cyber_wolf_report.html"):
        """
        Generate comprehensive HTML vulnerability report
        
        Args:
            results (dict): Scan results data
            filename (str): Output filename
            
        Returns:
            str: Path to generated report file
        """
        
        # Load HTML template
        template_path = os.path.join(self.template_dir, 'report.html')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            # Use inline template if file not found
            template_content = self._get_inline_template()
        
        # Create Jinja2 template
        template = Template(template_content)
        
        # Prepare data for template
        report_data = self._prepare_report_data(results)
        
        # Render template
        html_content = template.render(**report_data)
        
        # Write to file
        output_path = os.path.abspath(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _prepare_report_data(self, results):
        """Prepare data for template rendering"""
        
        # Group vulnerabilities by type
        vuln_by_type = {}
        for vuln in results['vulnerabilities']:
            vuln_type = vuln['type']
            if vuln_type not in vuln_by_type:
                vuln_by_type[vuln_type] = []
            vuln_by_type[vuln_type].append(vuln)
        
        # Calculate risk distribution
        risk_colors = {
            'high': '#dc3545',
            'medium': '#ffc107', 
            'low': '#28a745'
        }
        
        return {
            'results': results,
            'vulnerabilities_by_type': vuln_by_type,
            'risk_colors': risk_colors,
            'current_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'developer_info': {
                'name': 'S.Tamilselvan',
                'email': 'tamilselvanreacher@gmail.com',
                'portfolio': 'https://tamilselvan-portfolio-s.web.app/',
                'github': 'https://github.com/Tamilselvan-S-Cyber-Security'
            }
        }
    
    def _get_inline_template(self):
        """Fallback inline HTML template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Wolf Hunter - Vulnerability Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .wolf-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
        }
        .vulnerability-card {
            border-left: 4px solid;
            margin-bottom: 1rem;
        }
        .high-risk { border-left-color: #dc3545; }
        .medium-risk { border-left-color: #ffc107; }
        .low-risk { border-left-color: #28a745; }
        .stats-card {
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .wolf-logo {
            font-size: 3rem;
            margin-right: 1rem;
        }
        .footer-dev {
            background: #343a40;
            color: white;
            padding: 1rem 0;
            margin-top: 3rem;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="wolf-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col">
                    <h1><i class="fas fa-wolf-pack-battalion wolf-logo"></i>🐺 Cyber Wolf Hunter</h1>
                    <p class="lead mb-0">Comprehensive Website Vulnerability Assessment Report</p>
                </div>
            </div>
        </div>
    </div>

    <div class="container mt-4">
        <!-- Scan Summary -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card stats-card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="fas fa-chart-bar"></i> Scan Summary</h5>
                        <div class="row text-center">
                            <div class="col-md-2">
                                <h3 class="text-primary">{{ results.target }}</h3>
                                <small class="text-muted">Target URL</small>
                            </div>
                            <div class="col-md-2">
                                <h3 class="text-info">{{ results.statistics.vulnerabilities_found }}</h3>
                                <small class="text-muted">Total Issues</small>
                            </div>
                            <div class="col-md-2">
                                <h3 class="text-danger">{{ results.statistics.high_risk }}</h3>
                                <small class="text-muted">High Risk</small>
                            </div>
                            <div class="col-md-2">
                                <h3 class="text-warning">{{ results.statistics.medium_risk }}</h3>
                                <small class="text-muted">Medium Risk</small>
                            </div>
                            <div class="col-md-2">
                                <h3 class="text-success">{{ results.statistics.low_risk }}</h3>
                                <small class="text-muted">Low Risk</small>
                            </div>
                            <div class="col-md-2">
                                <h3 class="text-secondary">{{ results.scan_duration }}s</h3>
                                <small class="text-muted">Scan Time</small>
                            </div>
                        </div>
                        <hr>
                        <p><strong>Scan Date:</strong> {{ results.scan_time }}</p>
                        <p><strong>Report Generated:</strong> {{ current_time }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Vulnerabilities by Type -->
        {% for vuln_type, vulns in vulnerabilities_by_type.items() %}
        <div class="card mb-4">
            <div class="card-header">
                <h5><i class="fas fa-bug"></i> {{ vuln_type }} ({{ vulns|length }} issues)</h5>
            </div>
            <div class="card-body">
                {% for vuln in vulns %}
                <div class="vulnerability-card card mb-3 {{ vuln.risk_level }}-risk">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h6 class="card-title">
                                    <span class="badge bg-{{ 'danger' if vuln.risk_level == 'high' else ('warning' if vuln.risk_level == 'medium' else 'success') }}">
                                        {{ vuln.severity }}
                                    </span>
                                    {{ vuln.description }}
                                </h6>
                                <p class="card-text">
                                    <strong>URL:</strong> <code>{{ vuln.url }}</code><br>
                                    {% if vuln.payload %}
                                    <strong>Payload:</strong> <code>{{ vuln.payload }}</code><br>
                                    {% endif %}
                                    {% if vuln.parameter %}
                                    <strong>Parameter:</strong> <code>{{ vuln.parameter }}</code><br>
                                    {% endif %}
                                    <strong>Evidence:</strong> {{ vuln.evidence }}
                                </p>
                            </div>
                            <div class="col-md-4">
                                <div class="alert alert-info">
                                    <strong><i class="fas fa-lightbulb"></i> Recommendation:</strong><br>
                                    {{ vuln.recommendation }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}

        {% if not vulnerabilities_by_type %}
        <div class="alert alert-success text-center">
            <h4><i class="fas fa-shield-alt"></i> Great News!</h4>
            <p>No vulnerabilities were detected during the scan. Your website appears to be secure!</p>
        </div>
        {% endif %}
    </div>

    <!-- Footer -->
    <div class="footer-dev">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-code"></i> Developed By: {{ developer_info.name }}</h6>
                    <p class="mb-0">
                        <i class="fas fa-envelope"></i> {{ developer_info.email }}<br>
                        <i class="fas fa-globe"></i> <a href="{{ developer_info.portfolio }}" target="_blank" class="text-light">Portfolio</a> |
                        <i class="fab fa-github"></i> <a href="{{ developer_info.github }}" target="_blank" class="text-light">GitHub</a>
                    </p>
                </div>
                <div class="col-md-6 text-end">
                    <h6><i class="fas fa-wolf-pack-battalion"></i> Cyber Wolf Hunter v1.0</h6>
                    <p class="mb-0">Professional Website Security Assessment Tool</p>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        '''
