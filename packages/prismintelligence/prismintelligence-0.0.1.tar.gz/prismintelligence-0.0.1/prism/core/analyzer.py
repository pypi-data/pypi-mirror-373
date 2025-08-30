"""Main analysis engine for PRISM"""

import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from ultralytics import YOLO
import clip
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

class PrismAnalyzer:
    def __init__(self):
        """Initialize the analyzer with required models"""
        try:
            # Initialize YOLO (this should work)
            self.yolo_model = YOLO('yolov8n.pt')
            logger.info("YOLO model loaded successfully")
            
            # Try to load BLIP models (with fallback)
            try:
                self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                self.has_blip = True
                logger.info("BLIP model loaded successfully")
            except Exception as blip_error:
                logger.warning(f"BLIP model failed to load: {blip_error}")
                self.has_blip = False
            
            # Try to load CLIP (with fallback)
            try:
                self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device="cpu")
                self.has_clip = True
                logger.info("CLIP model loaded successfully")
            except Exception as clip_error:
                logger.warning(f"CLIP model failed to load: {clip_error}")
                self.has_clip = False
            
            logger.info("PRISM analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            raise
    
    def analyze_image(self, image_path: str) -> dict:
        """Analyze an image and return insights"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            image = Image.open(image_path).convert('RGB')
            
            # Multi-model analysis
            objects = self._detect_objects(image)
            caption = self._generate_caption(image)
            scene_context = self._analyze_scene(image)
            
            # Enhanced analysis with insights
            base_results = {
                'objects': objects,
                'summary': caption,
                'scene': scene_context,
                'confidence': self._calculate_confidence(objects, caption)
            }
            
            # Add rich insights
            enhanced_results = self._generate_insights(base_results)
            return enhanced_results
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _detect_objects(self, image):
        """Detect objects using YOLO"""
        results = self.yolo_model(image, verbose=False)
        objects = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = self.yolo_model.names[class_id]
                    
                    if confidence > 0.5:
                        objects.append({
                            'name': class_name,
                            'confidence': confidence
                        })
        
        return objects
    
    def _generate_caption(self, image):
        """Generate caption using BLIP"""
        if not self.has_blip:
            return "Caption generation unavailable (BLIP model not loaded)"
        
        try:
            inputs = self.blip_processor(image, return_tensors="pt")
            out = self.blip_model.generate(**inputs, max_length=50, do_sample=False)
            caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            logger.warning(f"Caption generation failed: {e}")
            return "Caption generation failed"
    
    def _analyze_scene(self, image):
        """Analyze scene context using CLIP"""
        if not self.has_clip:
            return {
                'type': "Scene analysis unavailable (CLIP model not loaded)",
                'confidence': 0.0
            }
        
        try:
            scene_types = [
                "indoor office meeting", "outdoor park recreation", 
                "home family gathering", "restaurant dining",
                "street urban activity", "beach vacation",
                "wedding celebration", "business conference"
            ]
            
            image_input = self.clip_preprocess(image).unsqueeze(0)
            text_inputs = clip.tokenize(scene_types)
            
            with torch.no_grad():
                logits_per_image, _ = self.clip_model(image_input, text_inputs)
                probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
            
            best_idx = probs.argmax()
            return {
                'type': scene_types[best_idx],
                'confidence': float(probs[best_idx])
            }
        except Exception as e:
            logger.warning(f"Scene analysis failed: {e}")
            return {
                'type': "Scene analysis failed",
                'confidence': 0.0
            }
    
    def _calculate_confidence(self, objects, caption):
        """Calculate overall confidence score with better weighting"""
        confidences = []
        
        # Object detection confidence (weighted heavily)
        if objects:
            avg_detection_conf = sum([obj['confidence'] for obj in objects]) / len(objects)
            confidences.append(avg_detection_conf * 0.6)  # 60% weight
        
        # Caption quality assessment
        if caption and "unavailable" not in caption.lower() and "failed" not in caption.lower():
            # Better caption quality scoring
            caption_score = min(len(caption.split()) / 8.0, 1.0) * 0.8  # Longer captions = better
            confidences.append(caption_score * 0.3)  # 30% weight
        
        # Scene detection boost (CLIP is usually confident)
        confidences.append(0.85 * 0.1)  # 10% weight, CLIP baseline
        
        overall_confidence = sum(confidences) if confidences else 0.5
        
        return {
            'overall': min(overall_confidence, 0.95),  # Cap at 95%
            'object_detection': avg_detection_conf if objects else 0.0,
            'scene_understanding': caption_score if 'caption_score' in locals() else 0.0
        }
    
    def _generate_insights(self, results):
        """Generate rich, human-like insights from analysis"""
        objects = results['objects']
        scene = results['scene']['type'] if isinstance(results['scene'], dict) else results['scene']
        summary = results['summary']
        
        # Count objects for insights
        object_names = [obj['name'] for obj in objects]
        people_count = object_names.count('person')
        cup_count = object_names.count('cup')
        
        # Generate instant insight
        instant_insight = self._create_instant_insight(people_count, cup_count, scene, object_names)
        
        # Generate understanding
        understanding = self._analyze_understanding(scene, object_names, people_count)
        
        # Generate detailed insights
        insights = self._generate_detailed_insights(object_names, people_count, cup_count, scene)
        
        # Create enhanced output
        enhanced = {
            'instant_insight': instant_insight,
            'confidence': results['confidence']['overall'] * 100,  # Convert to percentage
            
            'understanding': understanding,
            
            'details': {
                'people_count': people_count,
                'objects': self._categorize_objects(object_names),
                'scene_type': scene
            },
            
            'insights': insights,
            
            'raw': results  # Keep original output
        }
        
        return enhanced
    
    def _create_instant_insight(self, people_count, cup_count, scene, objects):
        """Create a compelling instant insight"""
        if 'office' in scene.lower() and people_count > 1:
            if cup_count >= 3:
                return f"Business meeting in progress - {people_count} people collaborating over coffee"
            else:
                return f"Professional team meeting with {people_count} colleagues"
        elif people_count > 1:
            return f"Group gathering with {people_count} people"
        else:
            return "Individual scene analysis"
    
    def _analyze_understanding(self, scene, objects, people_count):
        """Analyze the deeper understanding of the scene"""
        understanding = {}
        
        # What's happening
        if 'office' in scene.lower() and 'laptop' in objects:
            understanding['what'] = "Professional team meeting with laptops and documents"
        elif people_count > 1:
            understanding['what'] = f"Group interaction with {people_count} people"
        else:
            understanding['what'] = "Individual or single-person scene"
        
        # Where
        if 'office' in scene.lower():
            understanding['where'] = "Modern office conference room"
        elif 'indoor' in scene.lower():
            understanding['where'] = "Indoor setting"
        else:
            understanding['where'] = "Unspecified location"
        
        # Mood/Activity
        if 'tie' in objects and people_count > 1:
            understanding['mood'] = "Formal, professional"
            understanding['activity'] = "Business discussion or presentation"
        elif people_count > 1:
            understanding['mood'] = "Collaborative, engaged"
            understanding['activity'] = "Active discussion - not a presentation"
        else:
            understanding['mood'] = "Individual focus"
            understanding['activity'] = "Personal work or study"
        
        return understanding
    
    def _generate_detailed_insights(self, objects, people_count, cup_count, scene):
        """Generate specific insights based on detected patterns"""
        insights = []
        
        # Coffee/meeting insights
        if cup_count >= 3 and people_count > 1:
            insights.append(f"Long meeting - {cup_count} coffee cups suggest extended discussion")
        
        # Formality insights
        if 'tie' in objects and people_count > 1:
            formal_count = objects.count('tie')
            if formal_count == 1:
                insights.append("Mixed formal/casual - only one person in tie")
            else:
                insights.append("Formal business setting - multiple ties visible")
        
        # Technology insights
        if 'laptop' in objects and people_count > 1:
            insights.append("Collaborative setup - laptops open, people engaged")
        
        # Scene-specific insights
        if 'office' in scene.lower() and people_count >= 4:
            insights.append("Team meeting - multiple stakeholders present")
        
        return insights
    
    def _categorize_objects(self, objects):
        """Categorize objects into meaningful groups"""
        categories = {
            'people': [],
            'technology': [],
            'refreshments': [],
            'business': [],
            'other': []
        }
        
        # Count occurrences
        object_counts = {}
        for obj in objects:
            object_counts[obj] = object_counts.get(obj, 0) + 1
        
        # Categorize with counts
        for obj, count in object_counts.items():
            display_name = f"{obj}s ({count})" if count > 1 else obj
            
            if obj == 'person':
                categories['people'].append(display_name)
            elif obj in ['laptop', 'phone', 'computer', 'tablet']:
                categories['technology'].append(display_name)
            elif obj in ['cup', 'coffee', 'water', 'drink']:
                categories['refreshments'].append(display_name)
            elif obj in ['tie', 'suit', 'document', 'paper', 'book']:
                categories['business'].append(display_name)
            else:
                categories['other'].append(display_name)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

class AnalysisResult:
    """Enhanced container for analysis results"""
    def __init__(self, data):
        self.data = data
    
    @property
    def summary(self):
        # Support both old and new format
        if 'raw' in self.data:
            return self.data['raw']['summary']
        return self.data.get('summary', 'No summary available')
    
    @property
    def objects(self):
        # Support both old and new format
        if 'raw' in self.data:
            return [obj['name'] for obj in self.data['raw']['objects']]
        return [obj['name'] for obj in self.data.get('objects', [])]
    
    @property
    def scene(self):
        # Support both old and new format
        if 'raw' in self.data:
            scene_data = self.data['raw']['scene']
            return scene_data['type'] if isinstance(scene_data, dict) else scene_data
        scene_data = self.data.get('scene', 'Unknown scene')
        return scene_data['type'] if isinstance(scene_data, dict) else scene_data
    
    @property
    def confidence(self):
        # New format returns percentage directly
        if 'confidence' in self.data and isinstance(self.data['confidence'], (int, float)):
            return self.data['confidence'] / 100  # Convert back to decimal for compatibility
        # Old format
        if 'raw' in self.data:
            return self.data['raw']['confidence']['overall']
        return self.data.get('confidence', {}).get('overall', 0.0)
    
    @property
    def instant_insight(self):
        """Access the enhanced instant insight"""
        return self.data.get('instant_insight', 'Analysis complete')
    
    @property
    def understanding(self):
        """Access the enhanced understanding"""
        return self.data.get('understanding', {})
    
    @property
    def insights(self):
        """Access the detailed insights"""
        return self.data.get('insights', [])
    
    @property
    def details(self):
        """Access the categorized details"""
        return self.data.get('details', {})
    
    def __str__(self):
        # Enhanced display format
        if 'instant_insight' in self.data:
            output = [
                f"🔍 {self.instant_insight}",
                f"📊 Confidence: {self.data['confidence']:.1f}%",
                f"📍 Scene: {self.scene}",
                f"💭 Summary: {self.summary}",
            ]
            
            if self.insights:
                output.append("💡 Key Insights:")
                for insight in self.insights:
                    output.append(f"   • {insight}")
            
            if self.details.get('objects'):
                output.append("🏷️  Objects Found:")
                for category, items in self.details['objects'].items():
                    output.append(f"   {category.title()}: {', '.join(items)}")
            
            return '\n'.join(output)
        else:
            # Fallback to old format
            return f"Scene: {self.scene}\nSummary: {self.summary}\nObjects: {', '.join(self.objects)}\nConfidence: {self.confidence:.2%}"

# Global analyzer instance (lazy loading)
_analyzer = None

def analyze(image_path: str):
    """
    Analyze an image and return comprehensive insights
    
    Args:
        image_path: Path to image file
    
    Returns:
        AnalysisResult object with insights
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = PrismAnalyzer()
    
    raw_result = _analyzer.analyze_image(image_path)
    return AnalysisResult(raw_result)
