from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
import os
import pandas as pd
from io import BytesIO
import sys

# Import your existing processing engine
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from core.bulk_runner import run_bulk


app = Flask(__name__)
CORS(app)

# In-memory storage for manually added numbers
manual_numbers = []

UPLOAD_FOLDER = 'temp_uploads'
OUTPUT_FOLDER = 'temp_outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def create_formatted_excel(data, output_path):
    """Create a professionally formatted Excel file with styling"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Digital Footprint Results"
    
    # Define headers
    headers = ['Mobile Number', 'WhatsApp', 'Telegram', 'Instagram', 'Facebook', 'Snapchat', 'Checked On']
    ws.append(headers)
    
    # Style header row
    header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    # Define cell fills
    green_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
    red_fill = PatternFill(start_color="EF4444", end_color="EF4444", fill_type="solid")
    white_font = Font(bold=True, color="FFFFFF")
    
    # Add data rows
    for row_data in data:
        row = [
            row_data['mobile'],
            row_data['whatsapp'],
            row_data['telegram'],
            row_data['instagram'],
            row_data['facebook'],
            row_data['snapchat'],
            row_data['checked_on']
        ]
        ws.append(row)
        
        # Style the row
        current_row = ws.max_row
        
        # Style mobile number (first column)
        ws.cell(current_row, 1).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(current_row, 1).border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Style YES/NO columns (2-7)
        for col in range(2, 7):
            cell = ws.cell(current_row, col)
            value = cell.value
            
            if value == 'YES':
                cell.fill = green_fill
                cell.font = white_font
            elif value == 'NO':
                cell.fill = red_fill
                cell.font = white_font
            
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        
        # Style checked on date (last column)
        ws.cell(current_row, 7).alignment = Alignment(horizontal='center', vertical='center')
        ws.cell(current_row, 7).border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    # Auto-fit columns
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 4, 30)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Set row height for better visibility
    ws.row_dimensions[1].height = 25
    for row in range(2, ws.max_row + 1):
        ws.row_dimensions[row].height = 20
    
    wb.save(output_path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/add-number', methods=['POST'])
def add_number():
    """Add a mobile number to the in-memory list"""
    data = request.json
    number = data.get('number', '').strip()
    
    if not number:
        return jsonify({'success': False, 'message': 'Number is required'}), 400
    
    if number in manual_numbers:
        return jsonify({'success': False, 'message': 'Number already exists'}), 400
    
    manual_numbers.append(number)
    
    return jsonify({
        'success': True,
        'message': 'Number added successfully',
        'total': len(manual_numbers)
    })


@app.route('/api/get-numbers', methods=['GET'])
def get_numbers():
    """Get all manually added numbers"""
    return jsonify({
        'success': True,
        'numbers': manual_numbers,
        'total': len(manual_numbers)
    })


@app.route('/api/clear-numbers', methods=['POST'])
def clear_numbers():
    """Clear all manually added numbers"""
    manual_numbers.clear()
    return jsonify({
        'success': True,
        'message': 'All numbers cleared'
    })


@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Handle Excel file upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'message': 'Invalid file format. Use .xlsx or .xls'}), 400
    
    try:
        # Save uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'upload_{timestamp}.xlsx'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Read and validate
        df = pd.read_excel(filepath)
        
        if 'Mobile Number' not in df.columns:
            return jsonify({
                'success': False,
                'message': 'Excel must contain a "Mobile Number" column'
            }), 400
        
        numbers = df['Mobile Number'].dropna().astype(str).tolist()
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': filename,
            'count': len(numbers)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing file: {str(e)}'
        }), 500


@app.route('/api/process', methods=['POST'])
def process_numbers():
    """Process numbers and generate output Excel"""
    data = request.json
    uploaded_file = data.get('uploaded_file')
    
    try:
        # Determine input source
        if manual_numbers:
            # Create temporary input Excel from manual numbers
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            input_filename = f'input_{timestamp}.xlsx'
            input_path = os.path.join(UPLOAD_FOLDER, input_filename)
            
            df = pd.DataFrame({'Mobile Number': manual_numbers})
            df.to_excel(input_path, index=False)
        
        elif uploaded_file:
            # Use uploaded file
            input_path = os.path.join(UPLOAD_FOLDER, os.path.basename(uploaded_file))
        
        else:
            return jsonify({
                'success': False,
                'message': 'No numbers to process'
            }), 400
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'digital_footprint_results_{timestamp}.xlsx'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Call your existing processing engine
        run_bulk(input_path, output_path)
        
        # Read the results and reformat with styling
        df_results = pd.read_excel(output_path)
        
        # Convert to our format
        results_data = []
        for _, row in df_results.iterrows():
            results_data.append({
                'mobile': str(row['Mobile Number']),
                'whatsapp': row.get('WhatsApp', 'NO'),
                'telegram': row.get('Telegram', 'NO'),
                'instagram': row.get('Instagram', 'NO'),
                'facebook': row.get('Facebook', 'NO'),
                'snapchat': row.get('Snapchat', 'NO'),
                'checked_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Create formatted Excel
        formatted_output = os.path.join(OUTPUT_FOLDER, f'formatted_{output_filename}')
        create_formatted_excel(results_data, formatted_output)
        
        return jsonify({
            'success': True,
            'message': 'Processing complete',
            'output_file': f'formatted_{output_filename}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Processing error: {str(e)}'
        }), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download the generated Excel file"""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, os.path.basename(filename))
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Download error: {str(e)}'
        }), 404


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Digital Footprint Checker - Internal Tool")
    print("="*60)
    print("📍 Server running at: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
