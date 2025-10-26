from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
import re
import time

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Multi-language patterns and templates stay the same
FEEDBACK_TEMPLATES = {
    'english': {
        'confidence_high': 'Excellent speech! Very confident delivery.',
        'confidence_medium': 'Good speech with room for improvement.',
        'confidence_low': 'Your speech needs more practice for confidence.',
        'filler_words_feedback': 'Try to reduce filler words like: {}',
        'hesitation_feedback': 'Work on reducing hesitations in your speech',
        'repetition_feedback': 'Avoid repeating words frequently',
        'summary_template': 'Your speech was {} with a confidence score of {}%. {}',
        'areas_to_improve': 'Areas to improve:',
        'recommendations': 'Recommendations:',
        'analysis_summary': 'Analysis Summary',
        'speech_markers': 'Speech Markers',
        'hesitations': 'Hesitations',
        'repetitions': 'Repetitions',
        'filler_count': 'Filler Words',
        'start_button': 'Start',
        'stop_button': 'Stop',
        'analyze_button': 'Analyze Speech',
        'select_language': 'Select Language'
    },
    'telugu': {
        'confidence_high': 'అద్భుతమైన ప్రసంగం! చాలా ఆత్మవిశ్వాసంతో ఉంది.',
        'confidence_medium': 'మంచి ప్రసంగం, కానీ మెరుగుపరచుకోవలసిన అవకాశం ఉంది.',
        'confidence_low': 'ఆత్మవిశ్వాసం పెంచుకోవడానికి మరింత అభ్యాసం అవసరం.',
        'filler_words_feedback': 'ఈ పదాలు తగ్గించండి: {}',
        'hesitation_feedback': 'ఆగి ఆగి మాట్లాడటం తగ్గించండి',
        'repetition_feedback': 'పదాలను పదే పదే పునరావృతం చేయవద్దు',
        'summary_template': 'మీ ప్రసంగం {} మరియు ఆత్మవిశ్వాస స్కోరు {}%. {}',
        'areas_to_improve': 'మెరుగుపరచవలసిన అంశాలు:',
        'recommendations': 'సూచనలు:',
        'analysis_summary': 'విశ్లేషణ సారాంశం',
        'speech_markers': 'ప్రసంగ విశేషాలు',
        'hesitations': 'ఆగడాలు',
        'repetitions': 'పునరావృతాలు',
        'filler_count': 'అనవసర పదాలు',
        'start_button': 'ప్రారంభించు',
        'stop_button': 'ఆపు',
        'analyze_button': 'విశ్లేషించు',
        'select_language': 'భాష ఎంచుకోండి'
    },
    'hindi': {
        'confidence_high': 'बहुत बढ़िया भाषण! बहुत आत्मविश्वास के साथ।',
        'confidence_medium': 'अच्छा भाषण, लेकिन सुधार की गुंजाइश है।',
        'confidence_low': 'आत्मविश्वास बढ़ाने के लिए और अभ्यास की आवश्यकता है।',
        'filler_words_feedback': 'इन शब्दों का प्रयोग कम करें: {}',
        'hesitation_feedback': 'हिचकिचाहट को कम करें',
        'repetition_feedback': 'शब्दों की पुनरावृत्ति से बचें',
        'summary_template': 'आपका भाषण {} था और आत्मविश्वास स्कोर {}% था। {}',
        'areas_to_improve': 'सुधार के क्षेत्र:',
        'recommendations': 'सुझाव:',
        'analysis_summary': 'विश्लेषण सारांश',
        'speech_markers': 'भाषण के चिह्न',
        'hesitations': 'हिचकिचाहट',
        'repetitions': 'पुनरावृत्तियां',
        'filler_count': 'फिलर शब्द',
        'start_button': 'शुरू करें',
        'stop_button': 'रोकें',
        'analyze_button': 'विश्लेषण करें',
        'select_language': 'भाषा चुनें'
    }
}

LANGUAGE_PATTERNS = {
    'english': {
        'filler_words': [
            "uh", "um", "like", "you know", "I mean", "actually", "basically",
            "so", "well", "literally", "right", "kinda", "maybe", "just",
            "hmm", "let me see", "in fact", "to be honest", "sort of",
            "kind of", "I guess", "you see", "I suppose", "perhaps",
            "honestly", "to be frank", "not only that", "eventually"
        ],
        'hesitation_patterns': [r'\b(i+|u+h+|u+m+)\b', r'\.\.\.|…'],
        'repetition_pattern': r'\b(\w+)\s+\1\b'
    },
    'telugu': {
        'filler_words': [
            "అంటే", "మరి", "అదే", "చూడండి", "వినండి", "తెలుసా",
            "అలాగే", "సరే", "అవును", "కదా", "మీకు తెలుసా",
            "ఇలా", "అలా", "అబ్బా", "మరి చూడండి", "అయితే",
            "చెప్పాలంటే", "ఎందుకంటే", "అసలు", "నిజానికి", "ఏమో",
            "సరేగా", "మరేమో", "అవునుగా", "కానీ", "పోనీ",
            "ఇక్కడ", "అక్కడ", "ఎప్పుడైతే", "ఎలాగైతే"
        ],
        'hesitation_patterns': [r'\.\.\.', r'…'],
        'repetition_pattern': r'(\S+)\s+\1'
    },
    'hindi': {
        'filler_words': [
            "मतलब", "देखिए", "सुनिए", "तो", "ऐसे", "वैसे", "हाँ",
            "अच्छा", "ठीक है", "पता है", "समझे", "जैसे", "मैं कहूँ",
            "क्या है", "बात ये है", "यानी", "मैं कहूंगा", "देखो",
            "सुनो", "एक मिनट", "बताऊं", "मेरा मतलब", "असल में",
            "कैसे कहूं", "कुछ ऐसा", "लेकिन", "फिर भी", "और हाँ",
            "चलो", "अरे", "आप देखिये", "समझ लीजिए"
        ],
        'hesitation_patterns': [r'\.\.\.', r'…'],
        'repetition_pattern': r'(\S+)\s+\1'
    }
}

def analyze_confidence_markers(text, lang):
    markers = {
        'hesitations': 0,
        'repetitions': 0,
        'filler_words': 0,
        'weak_phrases': 0
    }
    
    patterns = LANGUAGE_PATTERNS[lang]
    
    # Count hesitations
    for pattern in patterns['hesitation_patterns']:
        markers['hesitations'] += len(re.findall(pattern, text.lower()))
    
    # Count word repetitions
    markers['repetitions'] = len(re.findall(patterns['repetition_pattern'], text.lower()))
    
    # Count filler words
    for word in patterns['filler_words']:
        markers['filler_words'] += len(re.findall(r'\b' + re.escape(word.lower()) + r'\b', text.lower()))
    
    return markers

def calculate_confidence_score(markers, text_length):
    weights = {
        'hesitations': 0.3,
        'repetitions': 0.25,
        'filler_words': 0.25,
        'weak_phrases': 0.2
    }
    
    if text_length == 0:
        return 1.0
        
    normalized_score = 1.0 - min(1.0, (
        sum(count * weights[marker] for marker, count in markers.items()) / 
        (text_length / 10)
    ))
    
    return max(0.0, normalized_score)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_ui_text', methods=['POST'])
def get_ui_text():
    data = request.get_json()
    user_lang = data.get('language', 'en')
    
    # Map browser language codes to our language codes
    lang_map = {
        'en': 'english',
        'te': 'telugu',
        'hi': 'hindi'
    }
    
    lang = lang_map.get(user_lang.lower(), 'english')
    templates = FEEDBACK_TEMPLATES[lang]
    
    return jsonify({
        'start_button': templates['start_button'],
        'stop_button': templates['stop_button'],
        'analyze_button': templates['analyze_button'],
        'select_language': templates['select_language']
    })

@app.route('/analyze', methods=['POST'])
@cache.memoize(timeout=300)
def analyze():
    try:
        start_time = time.time()
        print("Received analyze request")
        
        # Basic validation
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Get transcript and validate
        transcript = data.get('transcript', '').strip()
        if not transcript:
            return jsonify({"error": "No transcript provided"}), 400
        
        # Get language information
        user_lang = data.get('language', 'en').lower()
        language_segments = data.get('languageSegments', [])
        
        # Language mapping
        lang_map = {'en': 'english', 'te': 'telugu', 'hi': 'hindi'}
        default_lang = lang_map.get(user_lang, 'english')
        
        confidence_markers = {}
        confidence_score = 0
        segments = []
        
        if language_segments:
            # Multiple language analysis
            total_confidence = 0
            segment_count = 0
            overall_markers = {'hesitations': 0, 'repetitions': 0, 'filler_words': 0, 'weak_phrases': 0}
            
            for segment in language_segments:
                segment_lang = segment['language'].split('-')[0].lower()
                segment_lang_code = lang_map.get(segment_lang, default_lang)
                segment_text = segment['text'].strip()
                
                if segment_text:
                    segment_markers = analyze_confidence_markers(segment_text, segment_lang_code)
                    segment_confidence = calculate_confidence_score(segment_markers, len(segment_text.split()))
                    
                    total_confidence += segment_confidence
                    segment_count += 1
                    
                    for key in overall_markers:
                        overall_markers[key] += segment_markers.get(key, 0)
                    
                    if segment_confidence < 0.6:
                        segments.append({
                            "text": segment_text,
                            "confidence": segment_confidence,
                            "language": segment_lang_code,
                            "issues": [k for k, v in segment_markers.items() if v > 0]
                        })
            
            confidence_markers = overall_markers
            confidence_score = total_confidence / max(segment_count, 1)
        else:
            # Single language analysis
            confidence_markers = analyze_confidence_markers(transcript, default_lang)
            confidence_score = calculate_confidence_score(confidence_markers, len(transcript.split()))
            
            for sentence in [s.strip() for s in re.split(r'[.!?]+', transcript) if s.strip()]:
                local_markers = analyze_confidence_markers(sentence, default_lang)
                local_confidence = calculate_confidence_score(local_markers, len(sentence.split()))
                if local_confidence < 0.6:
                    segments.append({
                        "text": sentence,
                        "confidence": local_confidence,
                        "language": default_lang,
                        "issues": [k for k, v in local_markers.items() if v > 0]
                    })
        
        # Determine which language to use for overall templates/recommendations.
        # If multiple language segments exist, pick the dominant language by total words.
        templates_lang = default_lang
        if language_segments:
            # count words per language to pick dominant
            lang_word_counts = {}
            for seg in language_segments:
                seg_lang = seg['language'].split('-')[0].lower()
                seg_lang_code = lang_map.get(seg_lang, default_lang)
                seg_words = len(seg.get('text', '').split())
                lang_word_counts[seg_lang_code] = lang_word_counts.get(seg_lang_code, 0) + seg_words

            if lang_word_counts:
                # choose language with most words
                templates_lang = max(lang_word_counts.items(), key=lambda x: x[1])[0]

        # Get templates for response
        templates = FEEDBACK_TEMPLATES.get(templates_lang, FEEDBACK_TEMPLATES[default_lang])
        
        # Generate confidence feedback
        confidence_pct = round(confidence_score * 100, 2)
        if confidence_pct >= 80:
            confidence_feedback = templates['confidence_high']
        elif confidence_pct >= 60:
            confidence_feedback = templates['confidence_medium']
        else:
            confidence_feedback = templates['confidence_low']
        
        # Generate recommendations (use templates_lang for language-specific checks)
        recommendations = []
        words = transcript.split()
        try:
            filler_count = confidence_markers.get('filler_words', 0)
        except Exception:
            filler_count = 0

        if filler_count > len(words) * 0.1:
            used_fillers = [word for word in LANGUAGE_PATTERNS.get(templates_lang, LANGUAGE_PATTERNS[default_lang])['filler_words']
                          if re.findall(r'\b' + re.escape(word.lower()) + r'\b', transcript.lower())]
            if used_fillers:
                recommendations.append(templates['filler_words_feedback'].format(', '.join(used_fillers[:3])))

        if confidence_markers.get('hesitations', 0) > len(words) * 0.05:
            recommendations.append(templates['hesitation_feedback'])
        if confidence_markers.get('repetitions', 0) > len(words) * 0.05:
            recommendations.append(templates['repetition_feedback'])
        
        # Prepare response
        response = {
            "transcript": transcript,
            "language": default_lang,
            "confidence_score": confidence_pct,
            "confidence_feedback": confidence_feedback,
            "confidence_markers": confidence_markers,
            "low_confidence_segments": segments,
            "processing_time": round(time.time() - start_time, 3),
            "recommendations": recommendations,
            "templates": {
                "analysis_summary": templates['analysis_summary'],
                "speech_markers": templates['speech_markers'],
                "areas_to_improve": templates['areas_to_improve'],
                "recommendations": templates['recommendations'],
                "hesitations": templates['hesitations'],
                "repetitions": templates['repetitions'],
                "filler_count": templates['filler_count']
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)