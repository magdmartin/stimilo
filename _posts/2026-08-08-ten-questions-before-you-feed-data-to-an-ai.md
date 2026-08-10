---
layout: post
title: Ten questions to ask before you commit new data to an AI
description: A checklist written in 2019 for choosing a data source, reread for the era of agents acting on it.
date: 2026-08-08
categories: [notes]
tags: [data governance, AI, process]
---

Ten questions to ask before you commit to a data source. None of them are about extraction rules or code; they are about the governance of each feed — where it comes from, who stands behind it, how it was built, and what you are allowed to do with it.

[The list is from 2019](https://refinepro.com/blog/10-questions-to-ask-before-using-new-data/), written at RefinePro while we were ingesting hundreds of client data sources. It hasn't needed rewriting, just a different angle. 

**The consumer changed.** A feed used to land in a business system or on an analyst's desk. Now an agent acts on it.

A bad data source used to break the integration. Loudly: a schema shift, a failed job, an alert overnight. Someone looked at it. Feed the same source to a model and nothing breaks. It writes you a paragraph of half-truth, and the failure arrives silently downstream in a decision instead of upstream in a log.

## The ten questions

1. How was it collected?
2. How is it maintained?
3. Is it documented?
4. Does it follow standards?
5. Can you link it to another dataset?
6. Under what licence is the data available?
7. Are there privacy issues?
8. Who owns the data?
9. Who publishes it?
10. What are the format and granularity?

They sort now into four groups:

**Bias questions**. How the data was collected and how it is maintained tell you what is skewed, before a model generalises from it.

**AI accelerators**. Documentation, standards and linkage are what let a model understand your context instead of guessing at it.

**Hard limits**. They decide whether the data can go anywhere near a third party at all.

**General provenance checks**. They cover the who, the where and the what.

---
## Bias questions

### 1. How was it collected?

The answer tells you where the bias is. How was the data sampled, and what was left out? Which channel did the records arrive through, and does that shape them? Which population did nobody think to include? Is the data complete or partial? What was preprocessed, and under what conditions?

This used to be a question about interpretation: knowing the skew, you read the report accordingly. It is now a question about propagation. A model does not flag the gap. It infers a pattern from the rows that are there and answers confidently for the cases your data never covered. Unless you explicitly take it into account, nothing in the output distinguishes a real pattern from an artefact of how somebody collected a spreadsheet three years ago.

### 2. How is it maintained?

You need the update frequency, whether a pull returns the full set or only what changed, and whether the collection methodology has ever shifted. You also need to know whether the source will still be there next year.

This is the question that tells you if you are building on sand. Two failure modes matter more now than they used to. A methodology that changed partway through the history looks, to a model, like a real trend. And a feed that only returns recent changes means the history you think you have is a slice. Fine if you know it. Quietly wrong if you don't.

## AI accelerators

### 3. Is it documented?

Documentation should cover how the data was collected and how it should be interpreted: the schema, the data types, the validation rules. 

Good documentation guides the model to interpret the data correctly rather than infer it. Where it exists, you are handing over the definitions; where it doesn't, the model reconstructs them from the values, which is exactly the work you don't want it doing unsupervised.

Good documentation should answer most of the questions on this list without an email to the owner. 

### 4. Does it follow standards?

When data is collected and published to a standard, the ambiguity in collection, aggregation and preparation is already removed. Election data, [311 calls](http://open311.org/), census and [transit](https://developers.google.com/transit/gtfs) data are all standardised.

Standards are golden documentation for your LLM. They also let you compare oranges with oranges. More practically, they tell you when two datasets can be merged and when they have to be read separately. That judgment is cheap up front. It is expensive to discover after something has been built on the assumption they were the same.

### 5. Can you link it to another dataset?

Is this source isolated, or does it combine with something internal or external? Is there a shared key the model can use?

Shared identifiers turn a flat file into a graph. That graph is what a retrieval-augmented generation (RAG) setup searches when it assembles the context for an answer.

## Hard limits

### 6. Under what licence is the data available?

A licence defines how data can be collected, shared and used. For business data the terms sit in your contract or the provider's API terms of service; for public datasets they sit in an [open data licence](https://opendatacommons.org/licenses/). Sending a dataset to a model hosted by someone else is a form of sharing, and it may not be one those terms permit. Don't hand data you don't own, or aren't allowed to share, to somebody else's model.

### 7. Are there privacy issues?

Privacy protection differs by jurisdiction, with real differences between Canada, the United States and Europe. You need to know whether the data contains personally identifiable information, and whether individuals could be [re-identified from supposedly anonymised records](https://georgetownlawtechreview.org/re-identification-of-anonymized-data/GLTR-04-2017/). That risk did not stay flat. In a [2025 study](https://pubmed.ncbi.nlm.nih.gov/40502277/), an LLM re-identified 9% of clinical notes after the strongest de-identification tool tested had masked every piece of PII it could find.

Same warning as the licence question, higher stakes. Once the data leaves your systems it stops being a policy question.

## General provenance checks

### 8. Who owns the data?

Owning is not publishing. You need to know where the data originally comes from, who to contact when something looks wrong, and whose name goes on the attribution if the licence asks for one.

### 9. Who publishes it?

Platforms distribute datasets they do not own. Telling the owner and the publisher apart is what makes most of the other questions answerable.

### 10. What are the format and granularity?

Formats fall into a few groups: unstructured formats (PDF, web pages, documents, images), flat files (CSV, XLS), structured files (JSON, XML), APIs, and geographic formats (KML, Shapefile, GeoJSON). The format influences the model and token usage. 

Granularity is the lowest data point available. For time, that might be seconds or it might be years; for geography, an address or a country. It was always the limits on what you could ask of a dataset, and it still is. Monthly totals will not tell you what happened on a Tuesday. Ask a model anyway and it will produce something.

---

## Ask the ten before you connect the source

Every question here is answerable before anything gets built, most of them before you write a line of code, several in one conversation with whoever owns the feed.

Skip them and the work relocates. You end up troubleshooting hallucinations in the prompt, tuning context windows and rewriting instructions, for a problem that was decided upstream when somebody chose the source.

Knowing what data you need was never enough to start. You also need to know who your data is.

---

*This is a rewrite of [10 questions to ask before using new data](https://refinepro.com/blog/10-questions-to-ask-before-using-new-data/), first published on the RefinePro blog in 2020. The questions are unchanged. The reading is new.*

*Working on one of these? Happy to compare notes — [get in touch](/contact/).*
