# here is myllmservice.py

import logging

# logger = logging.getLogger(__name__)
import asyncio
from llmservice.base_service import BaseLLMService
from llmservice.generation_engine import GenerationRequest, GenerationResult
from typing import Optional, Union
import json
from  extracthero import prompts




class MyLLMService(BaseLLMService):
    def __init__(self, logger=None, max_concurrent_requests=200):
        super().__init__(
            logger=logging.getLogger(__name__),
            # default_model_name="gpt-4o-mini",
            default_model_name="gpt-4.1-nano",
            max_rpm=500,
            max_concurrent_requests=max_concurrent_requests,
        )
       
    


   
    
    
    def parse_via_llm(
        self,
        corpus: str,
        parse_keywords=None, 
        model = None,
    ) -> GenerationResult:
        
        
        user_prompt = prompts.PARSE_VIA_LLM_PROMPT.format(
            corpus=corpus,
            parse_keywords=parse_keywords,
           
        )
        

       
        
        pipeline_config = [
            {
                "type": "ConvertToDict",
                "params": {},
            }
        ]
       
        
        if model is None:
            model= "gpt-4o-mini"
            # model=  "gpt-4.1-nano"
          
           
        
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
           # formatted_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="parse_via_llm",
            pipeline_config=pipeline_config,
            # request_id=request_id,
        )

        result = self.execute_generation(generation_request)
        return result
    




    def analyze_individual_filter_prompt_experiment( self, experiment_data, model=None)-> GenerationResult:
        
        experiment_data= json.dumps(experiment_data, indent=2)

        user_prompt = prompts.PROMPT_analyze_individual_filter_prompt_experiment.format(
            experiment_data=experiment_data,
        
        )

       

      
    
         
        if model is None:
            model= "o3"
            
           
        
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
           # formatted_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="filter_via_llm",
            # pipeline_config=pipeline_config,
            # request_id=request_id,
        )

        result = self.execute_generation(generation_request)
        return result
    

    

    
    def analyze_filter_prompt_experiment_overall( self, merged_individual_results, model=None)-> GenerationResult:
        


        user_prompt = prompts.PROMPT_analyze_filter_prompt_experiment_overall.format(
            merged_individual_results=merged_individual_results,
        
        )

         
        if model is None:
            model= "o3"
            
        
        generation_request = GenerationRequest(
            user_prompt=user_prompt,
           # formatted_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="filter_via_llm",
            # pipeline_config=pipeline_config,
            # request_id=request_id,
        )

        result = self.execute_generation(generation_request)
        return result
    







    
    def filter_via_llm(
        self,
        corpus: str,
        thing_to_extract,
        model = None,
        filter_strategy=None
    ) -> GenerationResult:
        
     

       
        if filter_strategy=="liberal":
            user_prompt = prompts.PROPMT_filter_via_llm_liberal.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
        elif filter_strategy=="inclusive": 
            user_prompt = prompts.PROPMT_filter_via_llm_INCLUSIVE.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
        elif filter_strategy=="contextual":

            user_prompt = prompts.PROPMT_filter_via_llm_contextual.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )

        elif filter_strategy=="recall":
            user_prompt = prompts.PROPMT_filter_via_llm_recall.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
             
        elif filter_strategy=="base":
            user_prompt = prompts.PROPMT_filter_via_llm_base.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
        
    
    
        if model is None:
            #model= "gpt-4o-mini"
            
            model=  "gpt-4.1-nano"
        
        generation_request = GenerationRequest(
            # formatted_prompt=user_prompt,
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="filter_via_llm",
            # pipeline_config=pipeline_config,
            # request_id=request_id,
        )

        result = self.execute_generation(generation_request)
        return result
    
    





    async def filter_via_llm_async(
        self,
        corpus: str,
        thing_to_extract,
        model = None,
        filter_strategy=None
    ) -> GenerationResult:
        
        
       
        if filter_strategy=="liberal":
            user_prompt = prompts.PROPMT_filter_via_llm_liberal.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
        elif filter_strategy=="inclusive": 
            user_prompt = prompts.PROPMT_filter_via_llm_INCLUSIVE.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
        elif filter_strategy=="contextual":

            user_prompt = prompts.PROPMT_filter_via_llm_contextual.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )

        elif filter_strategy=="recall":
            user_prompt = prompts.PROPMT_filter_via_llm_recall.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
             
        else:
            user_prompt = prompts.PROPMT_filter_via_llm_base.format(
            corpus=corpus,
            thing_to_extract=thing_to_extract
   
            )
    
         
        if model is None:
            model= "gpt-4o-mini"

        generation_request = GenerationRequest(
            # formatted_prompt=user_prompt,
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="filter_via_llm",
            # pipeline_config=pipeline_config,
            # request_id=request_id,
        )

        # BaseLLMService already exposes an async runner:
        result = await self.execute_generation_async(generation_request)
        return result
    

    
        # ────────────────────────── async variant ──────────────────────────
    async def parse_via_llm_async(
        self,
        corpus: str,
        parse_keywords: list[str] | None = None,
        model: str | None = None,
    ) -> GenerationResult:
        """
        Non-blocking version of parse_via_llm().
        Requires BaseLLMService.execute_generation_async.
        """
        user_prompt = prompts.PARSE_VIA_LLM_PROMPT.format(
            corpus=corpus,
            parse_keywords=parse_keywords,
           
        )

        pipeline_config = [
            {"type": "ConvertToDict", "params": {}},
        ]

        model = model or "gpt-4o-mini"
        
        gen_request = GenerationRequest(
            # formatted_prompt=user_prompt,
            user_prompt=user_prompt,
            model=model,
            output_type="str",
            operation_name="parse_via_llm_async",
            pipeline_config=pipeline_config,
        )
    
        # BaseLLMService supplies execute_generation_async()
        return await self.execute_generation_async(gen_request)
    
    


    async def dummy_categorize_simple_async( self) -> GenerationResult:
        """
        Same prompt as categorize_simple, but issued through
        BaseLLMService.execute_generation_async so it can be awaited
        from an asyncio event-loop (e.g. your phase-3 pipeline).
        """
        user_prompt = """Here is list of classes: Food & Dining
                                                        Utilities
                                                        Accommodation
                                                        Incoming P2P Transfer
                                                        Outgoing P2P Transfers
                                                        Cash Withdrawal
                                                        Cash Deposit
                                                        Healthcare
                                                        Leisure and Activities in Real Life
                                                        Retail Purchases
                                                        Personal Care
                                                        Online Subscriptions & Services,
        

                            and here is string record to be classified:

                            pharmacy - eczane 30 dollars 28.05.24

                            Task Description:
                            Identify the Category: Determine which of the categories the string belongs to.
                            Extra Information - Helpers:  There might be additional information under each subcategory labeled as 'helpers'. These helpers include descs for the taxonomy,  but
                            should be considered as extra information and not directly involved in the classification task
                            Instructions:
                            Given the string record, first identify the category of the given string using given category list,  (your final answer shouldn't include words like "likely").
                            Use the 'Helpers' section for additional context.  And also at the end explain your reasoning in a very short way. 
                            Make sure category is selected from given categories and matches 100%
                            Examples:
                            Record: "Jumper Cable"
                            lvl1: interconnectors
                            
                            Record: "STM32"
                            lvl1: microcontrollers
        """
        
        pipeline_config = [
            {
                "type": "SemanticIsolation",
                "params": {"semantic_element_for_extraction": "pure category"},
            }
        ]

        generation_request = GenerationRequest(
            # formatted_prompt=formatted_prompt,
              user_prompt=user_prompt,
            model="gpt-4o-mini",
            output_type="str",
            operation_name="categorize_simple_async",
            pipeline_config=pipeline_config,
        )

        # BaseLLMService already exposes an async runner:
        result = await self.execute_generation_async(generation_request)
        return result



    
    def dummy_categorize_simple(self) -> GenerationResult:
        
        formatted_prompt = """Here is list of classes: Food & Dining
                                                        Utilities
                                                        Accommodation
                                                        Incoming P2P Transfer
                                                        Outgoing P2P Transfers
                                                        Cash Withdrawal
                                                        Cash Deposit
                                                        Healthcare
                                                        Leisure and Activities in Real Life
                                                        Retail Purchases
                                                        Personal Care
                                                        Online Subscriptions & Services,
        
                            and here is string record to be classified:  
                            
                            pharmacy - eczane 30 dollars 28.05.24

                            Task Description:
                            Identify the Category: Determine which of the categories the string belongs to.
                            Extra Information - Helpers:  There might be additional information under each subcategory labeled as 'helpers'. These helpers include descs for the taxonomy,  but
                            should be considered as extra information and not directly involved in the classification task
                            Instructions:
                            Given the string record, first identify the category of the given string using given category list,  (your final answer shouldnt include words like "likely").
                            Use the 'Helpers' section for additional context.  And also at the end explain your reasoning in a very short way. 
                            Make sure category is selected from given categories and matches 100%
                            Examples:
                            Record: "Jumper Cable"
                            lvl1: interconnectors
                            
                            Record: "STM32"
                            lvl1: microcontrollers
                             """


        pipeline_config = [
            {
                'type': 'SemanticIsolation',
                'params': {
                    'semantic_element_for_extraction': 'pure category'
                }
            }
        ]

        generation_request = GenerationRequest(
            formatted_prompt=formatted_prompt,
            model="gpt-4o-mini",
            output_type="str",
            operation_name="categorize_simple",
           pipeline_config= pipeline_config,
            
        )

        generation_result = self.execute_generation(generation_request)

    
        return generation_result



def main():
    """
    Main function to test the categorize_simple method of MyLLMService.
    """
    # Initialize the service
    my_llm_service = MyLLMService()

    # Sample data for testing
    sample_record = "The company reported a significant increase in revenue this quarter."
    sample_classes = ["Finance", "Marketing", "Operations", "Human Resources"]
    request_id = 1

    try:
        # Perform categorization
        result = my_llm_service.categorize_simple(
            record=sample_record,
            list_of_classes=sample_classes,
            request_id=request_id
        )

        # Print the result
        print("Generation Result:", result)
        if result.success:
            print("Categorized Content:", result.content)
        else:
            print("Error:", result.error_message)
    except Exception as e:
        print(f"An exception occurred: {e}")


if __name__ == "__main__":
    main()
