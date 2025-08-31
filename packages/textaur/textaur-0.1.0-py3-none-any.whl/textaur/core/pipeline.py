"""
Pipeline class to run linting process on input text.
"""
from .context import Context, Mode
from .textifier import Textifier, FileType, File
from .ai_linter import AILinter
from .strutil import Strutil

class Pipeline:
    """
    Pipeline class to run linting process on input text.
    """
    def __init__(
            self,
            log=print,
            progress_fn=lambda msg: print(f"\r{msg}", nl=False),
        ) -> None:
        """
        Initializes the pipeline.

        :param log
        Function to use for logging.

        :param progress_fn
        Function to use for progress updates.
        """
        self.log = log
        self.progress_fn = progress_fn
        self.textifier = Textifier(
            log=self.log,
            progress_fn=self.progress_fn,
        )
        self.strutil = Strutil(log=self.log)
        self.ai = AILinter()


    async def run(self, context: Context) -> None:
        """
        Runs the linting process on the input text.

        :param context
        Context object containing input and output file paths, mode, and other 
        options.
        """
        try:
            file = self.textifier.extract_text(
                file=context.input_file,
                use_ocr=context.use_ocr
            )
            if (file.filetype == FileType.UNSUPPORTED or not file.filetype
                or not (file.text or file.pages)):
                self.log("Unable to extract text. Sorry!")
                return
            # Save the extracted text only if it wasn't a text file
            if not file.filetype == FileType.TEXT:
                extracted = "".join(file.pages) if file.pages else file.text
                self.strutil.write_file(
                    path=context.extracted_text_file,
                    text=extracted,
                )
                self.log(f"Saved extracted text to: {context.extracted_text_file}")
            # if no lint, that's it
            if context.no_lint:
                return
            # lint, save, declare victory
            chunks = self._get_chunked(context, file)
            self.log(f"AI linting in a batch of {len(chunks)} pieces. This may take a while...")
            linted_text = await self._get_linted(context, chunks)
            self.log("AI linting complete.")
            self.strutil.write_file(path=context.output_file, text=linted_text)
            self.log(f"Saved linted text to: {context.output_file}")
            self.log("Finished!")
        except Exception as e:
            self.log(f"Encountered an unexpected error:\n{e}")


    def _get_chunked(self, context: Context, file: File) -> list[str]:
        """
        Splits the input text into chunks for linting.

        :param context
        Context object containing text mode.

        :param file
        File object containing the extracted text as pages or text.
        """
        if file.pages:
            chunks = self.strutil.chunk_pages(file.pages)
        elif file.text:
            # chunking files is different depending on the type of input text
            match context.mode:
                case Mode.SCREENPLAY:
                    chunk_fn = self.strutil.chunk_screenplay_text
                case _:
                    chunk_fn = self.strutil.chunk_generic_text
            chunks = chunk_fn(file.text)
        else:
            raise ValueError("Extracted text contains neither text nor pages.")
        return chunks


    async def _get_linted(self, context: Context, chunks: list[str]) -> str:
        """
        Lints the input text using the AI linter.

        :param context
        Context object containing input and output file paths, mode, and other 
        options.

        :param chunks
        List of text chunks to lint.
        """
        raw_linted = await self.ai.batch_lint_texts(chunks, context.prompt_text)
        return self._clean_up_raw_linted(
            context=context,
            text="\n".join(raw_linted),
        )


    def _clean_up_raw_linted(self, context: Context, text: str) -> str:
        """
        Cleans up the raw linted text.

        :param context
        Context object containing input and output file paths, mode, and other 
        options.

        :param text
        Raw linted text to clean up.
        """
        # future cleanup may vary depending on filetype
        return self.strutil.remove_consecutive_blank_lines(text)

