import gradio as gr

# Define a simple function
def greet(name):
    return f"Hello, {name}!"

# Create Gradio Interface
demo = gr.Interface(
    fn=greet, 
    inputs=gr.Textbox(placeholder="Enter your name here for me..."), 
    outputs="text",
    title="Simple Greeting App",
    description="Enter your name and get a greeting here and there!"
)

# Run the app
if __name__ == "__main__":
    #demo.launch(share=True)
    #demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
    demo.launch(server_name="0.0.0.0", server_port=7862, share=True, debug = True)


