--MODIFIERS--
--allergy
--lockbox
--heritage
--negated
--hypothetical
--leftover
--non-va
--medlist-current
--medlist-historical
--historical
--notpatient
--ra-oral
--ra-top
--ra-iv
--ra-im
--ra-inh
--ra-vag
--ra-sup
--ra-eye
--ra-ear

with negatedmention as (
	SELECT *
	FROM [DATABASE].[SCHEMA].[NLP_OUTPUT_TABLE]
	--Current project excludes all medication lists
	WHERE Modifier in ('allergy', 'historical', 'notpatient', 'negated', 'hypothetical', 'leftover', 'medlist-historical', 'medlist-current')
), negatedspans as (
	SELECT distinct o.*
	FROM [DATABASE].[SCHEMA].[NLP_OUTPUT_TABLE] o
	INNER JOIN negatedmention n on n.DocumentID = o.DocumentID and n.[Target] = o.[Target] AND
	--Overlapping span logic
	((n.Span_Start < o.Span_End AND n.Span_End > o.Span_Start) OR (o.Span_Start < n.Span_End AND o.Span_END > n.Span_Start))
), affirmedtargets as (
	SELECT DISTINCT o.DocumentID, o.[Target]
	FROM [DATABASE].[SCHEMA].[NLP_OUTPUT_TABLE] o
	LEFT JOIN negatedspans n ON n.DocumentID = o.DocumentID and n.Span_Start = o.Span_Start and n.Span_End = o.Span_End and n.[Target] = o.[Target] and n.Snippet = o.Snippet and n.Modifier = o.Modifier and n.Target_Code = o.Target_Code
	WHERE n.DocumentID IS NULL
)
SELECT DISTINCT
	DocumentID,
	NLP_ABX_flag = 1,
	stuff((
		select ',' + n.[Target]
		from affirmedtargets n
		where n.DocumentID = affirmedtargets.DocumentID
		order by n.[Target]
		for xml path('')
	),1,1,'') as AbxName
FROM affirmedtargets
GROUP BY DocumentID
;
