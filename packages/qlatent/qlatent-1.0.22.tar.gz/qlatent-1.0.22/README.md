# Indicators of Resilience (IoR)

In natural language processing (NLP), semantic relationships between words can be captured using  
a variety of different approaches, such as semantic word embeddings, transformer-based language models (a la BERT), encoder-decoder models (a la T5 and BART), and others.
While most embedding techniques consider the contexts of words, some consider sub-word components or even phonetics.[^1] 
Learning contextual language representations using transformers[^2] drove rapid progress in NLP and led to the development of tools readily accessible for researchers in a variety of disciplines.  
In this project, we refer to the various tools used to represent natural language collectively as **NLP models**.  

Most NLP models allow represeting words, phrases, sentences, and documents using mutidimentional coordinates, so called embedding. 
A vector in this coordinate system represents some concept. 
Similarity of concepts can be measured by, for example, the cosine similarity.[^3][^4]    
Coordinates of words may change depending on the language style, mood, and associations prevalent in the corpus on which the NLP models were trained.  


*Consider, for example, two chatbots - one trained using free text from the [SuicideWatch](https://www.reddit.com/r/SuicideWatch/) peer support group on Reddit and the other with free text from [partymusic](https://www.reddit.com/r/partymusic/) on the same platform. 
Intuitively, the answers of the two chatbots to the question `How do you feel today?` would be different. 
Now consider the kind of answers these two chatbots would provide to anxiety and depression questionnaires.*

The above example is overly simplistic in the sense that NLP models cannot be trained on the small amount of data of one subreddit, and the models' behavior depends on a variety of factors. 
We use this example only to illustrate the idea of querying an NLP model fitted to a corpus of messages produced by a specific population or after a specific event. 
Intuitively, the outputs of NLP models are biased toward associations prevalent in the training corpus.  

The main working hypothesis driving this library that **NLP models can capture – to a measurable extent – the emotional states reflected in the training corpus.**
Under the emotional state we include depression, exiety, stress and burnout. 
We also include the positive aspects of wellbeing such as sense of coherence,[^5] professional fulfillment,[^6] and various coping strategies[^7] all collectively referred to as **Indicators of Resilience (IoRs)**.   

Traditionally IoRs are measured using questionnairs such as [GAD](https://www.hiv.uw.edu/page/mental-health-screening/gad-2), [PHQ](https://www.hiv.uw.edu/page/mental-health-screening/phq-2), [SPF](https://wellmd.stanford.edu/self-assessment.html#professional-fulfillment), and others. 
This library provides the toolset and guidelines to translating validated psychological questionnairs into querried for trained NLP models.  


[^1]: Ling, S., Salazar, J., Liu, Y., Kirchhoff, K., & Amazon, A. (2020). Bertphone: Phonetically-aware encoder representations for utterance-level speaker and language recognition. In Proc. Odyssey 2020 the speaker and language recognition workshop (pp. 9-16).
[^2]: Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). Bert: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805.
[^3]: Mikolov, T., Sutskever, I., Chen, K., Corrado, G. S., & Dean, J. (2013). Distributed representations of words and phrases and their compositionality. In Advances in neural information processing systems (pp. 3111-3119).
[^4]: Caliskan, A., Bryson, J. J., & Narayanan, A. (2017). Semantics derived automatically from language corpora contain human-like biases. Science, 356(6334), 183-186.‏
[^5]: Antonovsky, A. (1987). Unraveling the mystery of health: How people manage stress and stay well. Jossey-bass.
[^6]: Trockel, M., Bohman, B., Lesure, E., Hamidi, M. S., Welle, D., Roberts, L., & Shanafelt, T. (2018). A brief instrument to assess both burnout and professional fulfillment in physicians: reliability and validity, including correlation with self-reported medical errors, in a sample of resident and practicing physicians. Academic Psychiatry, 42(1), 11-24.
[^7]: Lazarus, R. S., & Folkman, S. (1984). Stress, appraisal, and coping. Springer publishing company.
