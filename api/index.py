from flask import Flask, request, jsonify, render_template
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app

# This is the Vercel serverless function handler
def handler(request):
    with flask_app.request_context(request):
        return flask_app.full_dispatch_request()