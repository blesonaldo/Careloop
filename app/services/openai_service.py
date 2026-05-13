import os
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIService:
    """Service for generating AI-powered messages using OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPEN_AI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate_follow_up_message(
        self, 
        customer: Dict[str, Any], 
        user_name: str, 
        user_business: str
    ) -> str:
        """
        Generate a personalized follow-up message for a customer
        
        Args:
            customer: Customer information (name, phone, email, type, etc.)
            user_name: Name of the business owner
            user_business: Name of the business
            
        Returns:
            Generated follow-up message
        """
        
        # Create a personalized prompt based on customer type
        customer_type = customer.get('customer_type', 'new').lower()
        
        base_prompt = f"""
        You are a professional business assistant for {user_name} at {user_business}.
        
        Generate a personalized, friendly follow-up message for a customer:
        
        Customer Details:
        - Name: {customer.get('name', 'Valued Customer')}
        - Phone: {customer.get('phone_number', '')}
        - Email: {customer.get('email', '')}
        - Customer Type: {customer_type}
        - Business: {user_business}
        - Your Name: {user_name}
        
        Guidelines:
        - Keep it warm and personal (under 160 characters for SMS)
        - Mention their name for personalization
        - Reference their customer type appropriately
        - Include a clear call-to-action
        - Make it sound natural, not robotic
        - Include relevant emojis if appropriate
        - Focus on building the relationship
        """
        
        # Add specific instructions based on customer type
        if customer_type == 'new':
            base_prompt += """
            - Welcome them warmly
            - Thank them for their interest
            - Offer help or next steps
            """
        elif customer_type == 'active':
            base_prompt += """
            - Thank them for their business
            - Check if they need anything
            - Mention appreciation
            """
        elif customer_type == 'inactive':
            base_prompt += """
            - Gentle re-engagement
            - Mention you miss them
            - Offer special incentive if appropriate
            """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful business assistant that generates personalized follow-up messages. Always respond with just the message, no additional text."
                    },
                    {
                        "role": "user", 
                        "content": base_prompt
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            message = response.choices[0].message.content.strip()
            
            # Clean up the message (remove any quotes if present)
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
            
            return message
            
        except Exception as e:
            # Fallback message if OpenAI fails
            return f"Hi {customer.get('name', 'there')}! This is {user_name} from {user_business}. Just checking in to see how you're doing! 😊"
    
    async def generate_sales_message(
        self,
        customer: Dict[str, Any],
        product: str,
        user_name: str,
        user_business: str
    ) -> str:
        """
        Generate a sales-focused message for a customer
        
        Args:
            customer: Customer information
            product: Product/service being promoted
            user_name: Name of the business owner
            user_business: Name of the business
            
        Returns:
            Generated sales message
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful business assistant that generates sales messages. Always respond with just the message, no additional text."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Generate a compelling sales message for {customer.get('name', 'Valued Customer')} 
                        from {user_name} at {user_business} about {product}.
                        
                        Keep it:
                        - Under 160 characters for SMS
                        - Personal and engaging
                        - Include a clear call-to-action
                        - Add relevant emojis
                        """
                    }
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            message = response.choices[0].message.content.strip()
            
            # Clean up the message
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
            
            return message
            
        except Exception as e:
            return f"Hi {customer.get('name', 'there')}! {user_name} from {user_business} here. Thought you'd be interested in {product}. Let me know! 🎯"

# Singleton instance
openai_service = OpenAIService()
