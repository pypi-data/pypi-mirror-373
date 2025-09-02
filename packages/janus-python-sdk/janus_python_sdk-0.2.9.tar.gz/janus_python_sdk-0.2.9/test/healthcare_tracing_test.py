"""Healthcare Test: Demonstrating manual tracing with ADHD medication and treatment tool calls."""

import asyncio
import os
import time
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

import janus_sdk as janus
from janus_sdk import start_tool_event, finish_tool_event, record_tool_event, track

class HealthcareAgent:
    """Healthcare agent with manual tracing for medication and treatment tool calls."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self._turn = 0
        self.system_prompt = """You are a professional healthcare chatbot specializing in ADHD. 
        You have access to medication and treatment databases. Always provide evidence-based information 
        and recommend consulting with healthcare providers for specific medical advice. Keep responses under 200 tokens."""

    @track
    def analyze_symptom_severity(self, symptoms: list, impact_level: str) -> dict:
        """Analyze symptom severity and provide assessment score.
        
        This function is decorated with @track to demonstrate automatic tracing
        alongside manual tracing in the same application.
        """
        severity_scores = {
            "mild": 1-3,
            "moderate": 4-6, 
            "severe": 7-10
        }
        
        # Calculate symptom score based on number and type of symptoms
        base_score = len(symptoms) * 2
        
        # Adjust based on impact level
        impact_multiplier = {
            "work_and_social": 1.5,
            "academic": 1.3,
            "daily_life": 1.0
        }.get(impact_level, 1.0)
        
        final_score = min(10, int(base_score * impact_multiplier))
        
        # Determine severity category
        if final_score <= 3:
            severity = "mild"
        elif final_score <= 6:
            severity = "moderate"
        else:
            severity = "severe"
        
        return {
            "symptom_count": len(symptoms),
            "impact_level": impact_level,
            "severity_score": final_score,
            "severity_category": severity,
            "recommendation": f"Consider {severity} intervention strategies"
        }

    async def get_medication_info(self, medication_name: str) -> str:
        """Simulate getting medication information from a database."""
        # Start manual tracing for medication lookup
        handle = start_tool_event("medication_database", f"query: {medication_name}")
        
        try:
            # Simulate database query delay
            await asyncio.sleep(0.5)
            
            # Simulate medication database response
            if "methylphenidate" in medication_name.lower() or "ritalin" in medication_name.lower():
                result = "Methylphenidate (Ritalin): Stimulant medication, first-line treatment for ADHD. Common side effects: decreased appetite, insomnia, increased heart rate. Dosage: 5-60mg daily."
            elif "amphetamine" in medication_name.lower() or "adderall" in medication_name.lower():
                result = "Amphetamine (Adderall): Stimulant medication for ADHD. Side effects: nervousness, restlessness, dry mouth. Dosage: 5-40mg daily."
            elif "atomoxetine" in medication_name.lower() or "strattera" in medication_name.lower():
                result = "Atomoxetine (Strattera): Non-stimulant medication for ADHD. Side effects: nausea, fatigue, decreased appetite. Dosage: 40-100mg daily."
            elif "adhd" in medication_name.lower():
                result = "ADHD medications include stimulants (methylphenidate, amphetamines) and non-stimulants (atomoxetine, guanfacine). Each has different effects and side effects. Consult healthcare provider for personalized recommendations."
            else:
                result = f"Information for {medication_name}: Consult healthcare provider for specific medication details and dosing."
            
            # Finish tracing with success
            finish_tool_event(handle, result)
            return result
            
        except Exception as e:
            # Finish tracing with error
            finish_tool_event(handle, error=e)
            return f"Error retrieving medication information: {str(e)}"

    async def get_treatment_options(self, condition: str, patient_age: int = None) -> str:
        """Simulate getting treatment options from a medical database."""
        # Start manual tracing for treatment lookup
        handle = start_tool_event("treatment_database", f"condition: {condition}, age: {patient_age}")
        
        try:
            # Simulate database query delay
            await asyncio.sleep(0.3)
            
            # Simulate treatment database response
            if "adhd" in condition.lower():
                treatments = [
                    "Behavioral therapy and parent training",
                    "Stimulant medications (methylphenidate, amphetamine)",
                    "Non-stimulant medications (atomoxetine, guanfacine)",
                    "Educational accommodations and support",
                    "Lifestyle modifications (exercise, sleep hygiene)"
                ]
                result = f"ADHD treatment options: {'; '.join(treatments)}. Treatment choice depends on age, severity, and individual response."
            else:
                result = f"Treatment options for {condition}: Consult healthcare provider for personalized treatment plan."
            
            # Finish tracing with success
            finish_tool_event(handle, result)
            return result
            
        except Exception as e:
            # Finish tracing with error
            finish_tool_event(handle, error=e)
            return f"Error retrieving treatment options: {str(e)}"

    async def runner(self, prompt: str) -> str:
        """Main agent runner with manual tracing for healthcare tool calls."""
        self._turn += 1
        
        # Use @track decorated function to analyze symptoms (automatic tracing)
        symptoms = ["inattention", "hyperactivity", "impulsivity"]
        severity_analysis = self.analyze_symptom_severity(symptoms, "work_and_social")
        
        # Check if user is asking about medications
        if any(word in prompt.lower() for word in ["medication", "medicine", "drug", "pill", "ritalin", "adderall", "strattera"]):
            # Extract medication name from prompt
            medication_keywords = ["methylphenidate", "ritalin", "amphetamine", "adderall", "atomoxetine", "strattera"]
            medication_name = next((word for word in medication_keywords if word in prompt.lower()), "ADHD medication")
            
            # Get medication information with manual tracing
            medication_info = await self.get_medication_info(medication_name)
            
            # Use one-shot tracing for the response generation
            record_tool_event("response_generation", f"medication_query: {prompt}", "generating_response")
            
            # Generate response with medication info
            resp = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"User asked: {prompt}\n\nMedication information: {medication_info}\n\nProvide a helpful response incorporating this information."}
                ],
                max_tokens=150,
            )
            
        # Check if user is asking about treatment options
        elif any(word in prompt.lower() for word in ["treatment", "therapy", "options", "help", "manage", "cope"]):
            # Get treatment options with manual tracing
            treatment_info = await self.get_treatment_options("ADHD", patient_age=25)
            
            # Use one-shot tracing for the response generation
            record_tool_event("response_generation", f"treatment_query: {prompt}", "generating_response")
            
            # Generate response with treatment info
            resp = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"User asked: {prompt}\n\nTreatment options: {treatment_info}\n\nProvide a helpful response incorporating this information."}
                ],
                max_tokens=150,
            )
            
        else:
            # Regular response without tool calls
            record_tool_event("response_generation", f"general_query: {prompt}", "generating_response")
            
            resp = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
            )
        
        if resp.choices is None or not resp.choices:
            err = getattr(resp, "error", None) or resp.model_dump().get("error")
            raise RuntimeError(f"OpenAI API error: {err}")
        
        message = resp.choices[0].message
        answer = message.content
        return answer

async def main():
    """Run healthcare simulations with manual tracing."""
    


    await janus.run_simulations(
        num_simulations=5,
        max_turns=5,
        target_agent=lambda: HealthcareAgent().runner,
        api_key=os.getenv("JANUS_API_KEY")
    )

if __name__ == "__main__":
    asyncio.run(main()) 