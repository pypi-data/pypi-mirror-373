from typing import List  # , Union
from .tool_runner import ToolRunner
from nbitk.config import Config
import os


class Vsearch(ToolRunner):
    """
    A subclass of ToolRunner specifically for running Vsearch.

    This serves as base class for the Vsearch sub classes that are specific for
    different Vsearch operations like merging, filtering, dereplicating and denoising.

    Examples:

        >>> from nbitk.Tools.vsearch import Vsearch
        >>> from nbitk.config import Config

        >>> config = Config()
        >>> config.load_config('path/to/config.yaml')
        >>> vsearch_runner.set_params({
        >>>     "threads": "8",
        >>>     "maxaccepts": "10",
        >>>     "maxrejects": "5",
        >>>     "id": "0.97" })
        >>> return_code = vsearch_runner.run()
    """

    def __init__(self, config: Config):
        """
        Initialize the Vsearchrunner with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)
        self.tool_name = "vsearch"
    
    def set_threads(self, threads: int) -> None:
        """
        Set the number of threads to use.

        Args:
            threads (int): Number of CPU threads to use.

        Example:
            >>> vsearch_runner.set_threads(8)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"threads": str(threads)})
    
    def set_fastq_qmax(self, qmax: int = 50) -> None:
        """
        Set the maximum expected quality score.

        Args:
            qmax (int, optional): Maximum expected quality score. Defaults to 50.

        Example:
            >>> vsearch_runner.set_fastq_qmax(60)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_qmax": str(qmax)})
    
    def set_fastaout(self, fastaout: str) -> None:
        """
        Set the output fasta file.

        Args:
            fastaout (str): The path to the output fasta file.

        Example:
            >>> vsearch_runner.set_fastaout("path/to/output.fasta")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastaout": fastaout})    

    def set_fastqout(self, output: str) -> None:
        """
        Set the output file for the merged reads.

        Args:
            output (str): The path to the output file.

        Example:

            >>> from nbitk.Tools.vsearch import MergePairs
            >>> from nbitk.config import Config
            >>> vsearch_runner.set_fastqout("path/to/output.fastq")
            >>> vsearch_runner.run()

        Returns:
            None
        """    
        self.set_params({"fastqout": output})
    
    def set_sizein(self, sizein: bool = True) -> None:
        """
        retain abundance annotation from input.

        Args:
            sizein (bool): Whether to use the size information in the input.

        Example:
            >>> vsearch_runner.set_sizein(True)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        if sizein is True:
            self.set_params({"sizein": ""})

    def set_sizeout(self, sizeout: bool = True) -> None:
        """
        Set the sizeout parameter for Vsearch.

        Args:
            sizeout (bool): Whether to output the size of sequences.

        Example:
            >>> vsearch_runner.set_sizeout(True)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        if sizeout is True:
            self.set_params({"sizeout": ""})
    
    def set_fasta_width(self, fasta_width: int = 0) -> None:
        """
        Set the width of the fasta output.

        Args:
            fasta_width (int): The width of the fasta output.

        Example:
            >>> vsearch_runner.set_fasta_width(0)
            >>> vsearch_runner.run()
        Returns:
            None
        """
        self.set_params({"fasta_width": str(fasta_width)})
    
    def set_relabel_keep(self, relabel_keep: bool = True) -> None:
        """
        keep the old fasta label after the new when relabelling.

        Args:
            relabel_keep (bool): Whether to keep the original labels.

        Example:
            >>> vsearch_runner.set_relabel_keep(True)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        if relabel_keep is True:
            self.set_params({"relabel_keep": ""})

    def set_relabel_md5(self, relabel_md5: bool = True) -> None:
        """
        relabel sequences with md5 hash.

        Args:
            relabel_md5 (bool): Whether to relabel sequences with md5 hash.

        Example:
            >>> vsearch_runner.set_relabel_md5(True)
            >>> vsearch_runner.run()
        Returns:
            None
        """
        if relabel_md5 is True:
            self.set_params({"relabel_md5": ""})
    
    def set_relabel_prefix(self, relabel_prefix: str) -> None:
        """
        relabel sequences with prefix.

        Args:
            relabel_prefix (str): Prefix to use for relabelling.

        Example:
            >>> vsearch_runner.set_relabel_prefix("seq_")
            >>> vsearch_runner.run()
        Returns:
            None
        """
        self.set_params({"relabel": relabel_prefix})

    def set_relabel_sha1(self, relabel_sha1: bool = True) -> None:
        """
        relabel sequences with sha1 hash.

        Args:
            relabel_sha1 (bool): Whether to relabel sequences with sha1 hash.

        Example:
            >>> vsearch_runner.set_relabel_sha1(True)
            >>> vsearch_runner.run()
        Returns:
            None
        """
        if relabel_sha1 is True:
            self.set_params({"relabel_sha1": ""})
    
    def set_otutabout(self, otutabout: str) -> None:
        """
        write OTU table to file.

        Args:
            otutabout (str): The path to the output file.

        Example:
            >>> vsearch_runner.set_otutabout("path/to/output.tsv")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"otutabout": otutabout})
    
    def set_database(self, database: str) -> None:
        """
        name of UDB or FASTA database for search.

        Args:
            database (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(database), f"Input  file not found: {database}"
        self.set_params({"db": database})
    
    def set_id(self, id: float) -> None:
        """
        Set the identity threshold for clustering.
        Reject if identity lower, accepted values: 0-1.0

        Args:
            id (float): The identity threshold for clustering.
        
        Returns:
            None        
        """
        self.set_params({"id": str(id)})

    
    def set_params(self, params: dict) -> None:
        """
        Set multiple command-line parameters for Vsearch.

        Args:
            params (dict): A dictionary where keys are parameter names (str) and
                        values are the parameter value (str or any type that
                        can be converted to a string).

        Example:

            >>> from nbitk.Tools.vsearch import Vsearch
            >>> from nbitk.config import Config # could also load params from a confing
            >>> vsearch_runner.set_params({
            >>>     "threads": "8",
            >>>     "maxaccepts": "10",
            >>>     "maxrejects": "5",
            >>>     "id": "0.97"
            >>> })
            >>> vsearch_runner.run()

            This will call `set_parameter` for each parameter in the dictionary,
            setting them for the Vsearch tool instance.

        Returns:
            None
        """
        vsearch_valid_params = self.get_valid_tool_params("--help")
        for param, value in params.items():
            try:
                assert f'--{param}' in vsearch_valid_params, f"{param} is not a valid {self.tool_name} parameter"
                self.set_parameter(param, value)
                self.logger.info(f"Set parameter --{param} to {value}")
            except AssertionError as e:
                self.logger.error(str(e))
                raise

    def build_command(self) -> List[str]:
        """
        Build the vsearch merge fastq command with all set parameters.

        :return: The complete command as a list of strings.
        :rtype: List[str]
        """
        command = super().build_command()

        return command

    @staticmethod
    def long_arg_prefix() -> str:
        """
        Get the appropriate prefix for a long command-line argument

        :return: The appropriate prefix for a long argument
        :rtype: str
        """
        return "--"

class MergePairs(Vsearch):
    """
    A sub class of Vsearch specific for merging pairs
    """
    
    def __init__(self, config: Config):
        """
        Initialize the MergePairs with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)

    def set_pairs(self, forward: str, reverse: str) -> None:
        """
        Set the forward and reverse read pairs for merging.

        Args:
            forward (str): The path to the forward read file.
            reverse (str): The path to the reverse read file.

        Example:

            >>> from nbitk.Tools.vsearch import MergePairs
            >>> from nbitk.config import Config
            >>> vsearch_runner.set_pairs("path/to/forward.fastq", "path/to/reverse.fastq")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        assert os.path.exists(forward), f"Forward reads file not found: {forward}"
        assert os.path.exists(reverse), f"Reverse reads file not found: {reverse}"
        
        self.set_params({"fastq_mergepairs": forward})
        self.set_params({"reverse": reverse})

    

    def set_maxdiffpct(self, maxdiffpct: int) -> None:
        """
        Set the maximum percentage difference for merging.

        Args:
            maxdiffpct (int): Maximum percentage of mismatches allowed in the overlap region.

        Example:
            >>> vsearch_runner.set_maxdiffpct(5)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_maxdiffpct": str(maxdiffpct)})

    def set_maxdiffs(self, maxdiffs: int) -> None:
        """
        Set the maximum number of differences allowed in the overlap region.

        Args:
            maxdiffs (int): Maximum number of mismatches allowed in the overlap region.

        Example:
            >>> vsearch_runner.set_maxdiffs(10)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_maxdiffs": str(maxdiffs)})

    def set_minovlen(self, minovlen: int) -> None:
        """
        Set the minimum overlap length for merging.

        Args:
            minovlen (int): Minimum length of overlap required for merging.

        Example:
            >>> vsearch_runner.set_minovlen(20)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_minovlen": str(minovlen)})


    def set_allowmergestagger(self, allowmergestagger: bool = True) -> None:
        """
        Allow merge stagger, i.e. reads that do not fully overlap.

        Example:
            >>> vsearch_runner.set_allowmergestagger()
            >>> vsearch_runner.run()

        Returns:
            None
        """
        if allowmergestagger is True:
            self.set_params({"fastq_allowmergestagger": ""})
    
    def set_fastq_qminout(self, qminout: int) -> None:
        """
        Set the minimum base quality value for FASTQ output.

        Args:
            qminout (int): Minimum quality score for output reads.

        Example:
            >>> vsearch_runner.set_fastq_qminout(20)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_qminout": str(qminout)})
    def set_fastq_minmergelen(self, minmergelen: int) -> None:
        """
        Set the minimum length of merged reads.

        Args:
            minmergelen (int): Minimum length of merged reads.

        Example:
            >>> vsearch_runner.set_fastq_minmergelen(200)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_minmergelen": str(minmergelen)})



class Filter(Vsearch):
    """
    A sub class of Vsearch specific for filtering reads
    """

    def __init__(self, config: Config):
        """
        Initialize the Filter with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)

    def set_fastq_filter(self, fastq_filter: str) -> None:
        """
        Set the input fastq file to filter.

        Args:
            fastq_filter (str): The path to the input fastq file.

        Example:
            >>> vsearch_runner.set_fastq_filter("path/to/input.fastq")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        assert os.path.exists(fastq_filter), f"Input fastq file not found: {fastq_filter}"
        self.set_params({"fastq_filter": fastq_filter})
    
    
    def set_fastq_minlen(self, minlen: int) -> None:
        """
        Set the minimum length of reads to keep.

        Args:
            minlen (int): Minimum length of reads to keep.

        Example:
            >>> vsearch_runner.set_minlen(100)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_minlen": str(minlen)})

    def set_fastq_maxlen(self, maxlen: int) -> None:
        """
        Set the maximum length of reads to keep.

        Args:
            maxlen (int): Maximum length of reads to keep.

        Example:
            >>> vsearch_runner.set_maxlen(300)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_maxlen": str(maxlen)})

    def set_fastq_maxee(self, maxee: int) -> None:
        """
        Set the maximum expected error rate for reads to keep.

        Args:
            maxee (int): Maximum expected error rate for reads to keep.

        Example:
            >>> vsearch_runner.set_maxee(1)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_maxee": str(maxee)})

    def set_fastq_truncqual(self, truncqual: int) -> None:
        """
        Set the quality score threshold for truncating reads.

        Args:
            truncqual (int): Quality score threshold for truncating reads.

        Example:
            >>> vsearch_runner.set_truncqual(20)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_truncqual": str(truncqual)})
    
    def set_fastq_maxns(self, maxns: int) -> None:
        """
        Set the maximum number of Ns allowed in a read.

        Args:
            maxns (int): Maximum number of Ns allowed in a read.

        Example:
            >>> vsearch_runner.set_fastq_maxns(0)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_maxns": str(maxns)})
    
    def set_fastq_minsize(self, minsize: int) -> None:
        """
        Set the minimum size of reads to keep.

        Args:
            minsize (int): Minimum size of reads to keep.

        Example:
            >>> vsearch_runner.set_minsize(200)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"fastq_minsize": str(minsize)})


class Dereplicate(Vsearch):
    """
    A sub class of Vsearch specific for dereplicating reads
    """
    
    def __init__(self, config: Config):
        """
        Initialize the Dereplicate with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)
    

    def set_fastx_uniques(self, fastx_uniques: str) -> None:
        """
        Set the input fasta or fastq  file to dereplicate.

        Args:
            fastx_uniques (str): The path to the input fasta/fastq file.

        Example:
            >>> vsearch_runner.set_fastx_uniques("path/to/input.fasta")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        assert os.path.exists(fastx_uniques), f"Input  file not found: {fastx_uniques}"
        self.set_params({"fastx_uniques": fastx_uniques})

    def set_output(self, output: str) -> None:
        """
        Set the output file for dereplicated reads.
        (use fastqout for fastq output and fastaout for fasta output)

        Args:
            output (str): The path to the output file.

        Example:
            >>> vsearch_runner.set_output("path/to/output.fasta")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"output": output})

    def set_derep_fulllength(self, derep_fulllength: bool = True) -> None:
        """
        Set the derep_fulllength parameter for Vsearch.

        Args:
            derep_fulllength (bool): Whether to dereplicate full length sequences.

        Example:
            >>> vsearch_runner.set_derep_fulllength(True)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        if derep_fulllength is True:
            self.set_params({"derep_fulllength": ""})

    def set_derep_prefix(self, derep_prefix: str) -> None:
        """
        Dereplicate sequences in file based on prefixes.

        Args:
            derep_prefix (str): file path to dereplicate.

        Example:
            >>> vsearch_runner.set_derep_prefix("derep_")
            >>> vsearch_runner.run()"
            "Returns:
            None
        """   
        self.set_params({"derep_prefix": derep_prefix})
    
    def set_derep_id(self, derep_id: str) -> None:
        """
        dereplicate using both identifiers and sequences.

        Args:
            derep_id (path): file to dereplicate.

        Example:
            >>> vsearch_runner.set_derep_id(path/to/derep_file)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"derep_id": derep_id})
    def set_minuniquesize(self, minuniquesize: int) -> None:
        """
        Set the minimum unique size of reads to keep.

        Args:
            minuniquesize (int): Minimum unique size of reads to keep.

        Example:
            >>> vsearch_runner.set_minuniquesize(200)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"minuniquesize": str(minuniquesize)})
    
    def set_tabbedout(self, tabbedout: str) -> None:
        """
        write cluster info to tsv file for fastx_uniques.

        Args:
            tabbedout (str): The path to the tabbed output file.

        Example:
            >>> vsearch_runner.set_tabbedout("path/to/output.tsv")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"tabbedout": tabbedout})

class Denoise(Vsearch):
    """
    A sub class of Vsearch specific for denoising/clustering reads
    """
    
    def __init__(self, config: Config):
        """
        Initialize the Denoise with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)
    
    def set_cluster_unoise(self, cluster_unoise: str) -> None:
        """
        denoise Illumina/AVITI amplicon reads.

        Args:
            cluster_unoise (str): The path to the input fasta/fastq
        Returns:
            None
        """
        assert os.path.exists(cluster_unoise), f"Input  file not found: {cluster_unoise}"
        self.set_params({"cluster_unoise": cluster_unoise})
    
    def set_cluster_size(self, cluster_size: str) -> None:
        """
        cluster sequences after sorting by abundance.

        Args:
            cluster_size (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(cluster_size), f"Input  file not found: {cluster_size}"
        self.set_params({"cluster_size": cluster_size})
    
    def set_cluster_fast(self, cluster_fast: str) -> None:
        """
        cluster sequences after sorting by length.

        Args:
            cluster_fast (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(cluster_fast), f"Input  file not found: {cluster_fast}"
        self.set_params({"cluster_fast": cluster_fast})
    
    def set_unoise_alpha(self, unoise_alpha: float) -> None:
        """
        Set the alpha parameter for unoise.

        Args:
            unoise_alpha (float): The alpha parameter for unoise.
        
        Returns:
            None        
        """
        self.set_params({"unoise_alpha": str(unoise_alpha)})

    def set_minsize(self, minsize: int) -> None:
        """
        Set minimum abundance (unoise only) (default: 8).

        Args:
            minsize (int): Minimum size of reads to keep.

        Example:
            >>> vsearch_runner.set_minsize(8)
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"minsize": str(minsize)})
    

    def set_centroids(self, centroids: str) -> None:
        """
        output centroid sequences to FASTA file.

        Args:
            centroids (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"centroids": centroids})
    
    def set_size_order(self, size_order: bool) -> None:
        """
        Sort sequences by ssort accepted centroids by abundance.

        Args:
            size_order (bool): Whether to sort sequences by size before clustering.
        
        Returns:
            None        
        """
        if size_order is True:
            self.set_params({"sizeorder": ""})
    
    
    
    def set_clusters(self, clusters: str) -> None:
        """
        output each cluster to a separate FASTA file.

        Args:
            clusters (str): The path to the output file.

        Example:
            >>> vsearch_runner.set_clusters("path/to/output.tsv")
            >>> vsearch_runner.run()
        returns:
            None
        """
        self.set_params({"clusters": clusters})
    
    def set_msaout(self, msaout: str) -> None:
        """
        write multiple sequence alignment to file.

        Args:
            msaout (str): The path to the output file.

        Example:
            >>> vsearch_runner.set_msaout("path/to/output.fasta")
            >>> vsearch_runner.run()

        Returns:
            None
        """
        self.set_params({"msaout": msaout})

    
class removeChimera(Vsearch):
    """
    A sub class of Vsearch specific for removing chimeras
    """
    def __init__(self, config: Config):
        """
        Initialize the removeChimera with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)

    def set_uchime_denovo(self, uchime_denovo: str) -> None:
        """
        remove chimeras using de novo method.

        Args:
            uchime_denovo (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(uchime_denovo), f"Input  file not found: {uchime_denovo}"
        self.set_params({"uchime_denovo": uchime_denovo})
    
    def set_uchime2_denovo(self, uchime2_denovo: str) -> None:
        """
        detect chimeras de novo in denoised amplicons.

        Args:
            uchime2_denovo (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(uchime2_denovo), f"Input  file not found: {uchime2_denovo}"
        self.set_params({"uchime2_denovo": uchime2_denovo})
    def set_uchime3_denovo(self, uchime3_denovo: str) -> None:
        """
        detect chimeras de novo in denoised amplicons.

        Args:
            uchime3_denovo (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(uchime3_denovo), f"Input  file not found: {uchime3_denovo}"
        self.set_params({"uchime3_denovo": uchime3_denovo})
    
    def set_uchime_ref(self, uchime_ref_file: str) -> None:
        """
        remove chimeras using reference database.

        Args:
            uchime_ref (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(uchime_ref_file), f"Input  file not found: {uchime_ref_file}"
        self.set_params({"uchime_ref": uchime_ref_file})
    
    def set_uchime_db(self, db: str) -> None:
        """
        set the reference database for chimera removal.

        Args:
            db (str): The path to the reference database.
        
        Returns:
            None        
        """
        assert os.path.exists(db), f"Reference database file not found: {db}"
        self.set_params({"db": db})
    def set_mindiffs(self, mindiffs: int) -> None:
        """
        Set the minimum number of differences for chimera removal.

        Args:
            mindiffs (int): Minimum number of differences for chimera removal.
        
        Returns:
            None        
        """
        self.set_params({"mindiffs": str(mindiffs)})
    
    def set_borderline(self, borderline: str) -> None:
        """
        output borderline chimeric sequences to file.

        Args:
            borderline (str): file path to output borderline chimeras.
        
        Returns:
            None        
        """
        self.set_params({"borderline": borderline})
    
    def set_chimeras(self, chimeras: str) -> None:
        """
        output chimeric sequences to file.

        Args:
            chimeras (str): file path to output chimeras.
        
        Returns:
            None        
        """
        self.set_params({"chimeras": chimeras})
    
    def set_nonchimeras(self, nonchimeras: str) -> None:
        """
        output non-chimeric sequences to file.

        Args:
            nonchimeras (str): file path to output non-chimeras.
        
        Returns:
            None        
        """
        self.set_params({"nonchimeras": nonchimeras})
    
    def uchimealns(self, uchimealns: str) -> None:
        """
        write multiple sequence alignment to file.

        Args:
            uchimealns (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"uchimealns": uchimealns})
    
    def set_uchimeout(self, uchimeout: str) -> None:
        """
        write chimera detection info to file.

        Args:
            uchimeout (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"uchimeout": uchimeout})
    
    def set_fasta_score(self, fasta_score: bool = True) -> None:
        """
        include chimera score in FASTA output.

        Args:
            chimeras_fasta_score (str): The path to the output file.
        
        Returns:
            None        
        """
        if fasta_score is True:
            self.set_params({"fasta_score": ""})


class Search(Vsearch):
    """
    A sub class of Vsearch specific for searching reads
    """

    def __init__(self, config: Config):
        """
        Initialize the Search with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)

    def set_search_exact(self, search_exact: str) -> None:
        """
        set filename of queries for exact match search.

        Args:
            search_exact (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(search_exact), f"Input  file not found: {search_exact}"
        self.set_params({"search_exact": search_exact})
    
    def set_search_global(self, search_global: str) -> None:
        """
        set filename of queries for global search.

        Args:
            search_global (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(search_global), f"Input  file not found: {search_global}"
        self.set_params({"usearch_global": search_global})
    
        
    def set_maxhits(self, maxhits: int) -> None:
        """
        set maximum number of hits to report.

        Args:
            maxhits (int): Maximum number of hits to report.
        
        Returns:
            None        
        """
        self.set_params({"maxhits": str(maxhits)})

    def set_output_no_hits(self, output_no_hits: bool = True) -> None:
        """
        write sequences with no hits to file.

        Args:
            output_no_hits (str): The path to the output file.
        
        Returns:
            None        
        """
        if output_no_hits is True:
            self.set_params({"output_no_hits": ""})
    
    def set_mintsize(self, mintsize: int) -> None:
        """
        set minimum target size for search.
        reject if target abundance lower.

        Args:
            mintsize (int): Minimum target size for search.
        
        Returns:
            None        
        """
        self.set_params({"mintsize": str(mintsize)})
    
    def set_wordlength(self, wordlength: int) -> None:
        """
        length of words for database index 3-15 (default = 8).

        Args:
            wordlength (int): Word length for search.
        
        Returns:
            None        
        """
        self.set_params({"wordlength": str(wordlength)})
    
    def set_fastapairs(self, fastapairs: str) -> None:
        """
        write matching pairs to file.

        Args:
            fastapairs (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"fastapairs": fastapairs})

    def set_notmatched(self, notmatched: str) -> None:
        """
        write sequences with no hits to file.

        Args:
            notmatched (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"notmatched": notmatched})

    def set_matched(self, matched: str) -> None:
        """
        write sequences with hits to file.

        Args:
            matched (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"matched": matched})
    
    def set_lca_cutoff(self, lca_cutoff: int) -> None:
        """
        set LCA cutoff for taxonomic assignment.

        Args:
            lca_cutoff (int): LCA cutoff for taxonomic assignment.
        
        Returns:
            None        
        """
        self.set_params({"lca_cutoff": str(lca_cutoff)})
    
    def set_lcaout(self, lcaout: str) -> None:
        """
        output LCA of matching sequences to file.

        Args:
            lcaout (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"lcaout": lcaout})
    
    def set_mismatch_score(self, mismatch_score: int) -> None:
        """
        set mismatch score for alignment (default: -4).

        Args:
            mismatch_score (int): Mismatch score for alignment.
        
        Returns:
            None        
        """
        self.set_params({"mismatch": str(mismatch_score)})
    
    def set_minwordmatches(self, minwordmatches: int) -> None:
        """
        set minimum number of word matches (default: = 12).

        Args:
            minwordmatches (int): Minimum number of word matches.
        
        Returns:
            None        
        """
        self.set_params({"minwordmatches": str(minwordmatches)})

    def set_gapopen(self, gapopen: int) -> None:
        """
        set gap open penalty for alignment.

        Args:
            gapopen (int): Gap open penalty for alignment.
        
        Returns:
            None        
        """
        self.set_params({"gapopen": str(gapopen)})
    
    def set_maxgaps(self, maxgaps: int) -> None:
        """
        set maximum number of gaps for alignment.

        Args:
            maxgaps (int): Maximum number of gaps for alignment.
        
        Returns:
            None        
        """
        self.set_params({"maxgaps": str(maxgaps)})
    
    def set_maxsubs(self, maxsubs: int) -> None:
        """
        set maximum number of substitutions for alignment.

        Args:
            maxsubs (int): Maximum number of substitutions for alignment.
        
        Returns:
            None        
        """
        self.set_params({"maxsubs": str(maxsubs)})
    
    def set_query_cov(self, query_cov: float) -> None:
        """
        set minimum query coverage for alignment.

        Args:
            query_cov (float): Minimum query coverage for alignment.
        
        Returns:
            None        
        """
        self.set_params({"query_cov": str(query_cov)})
    
    def set_dbmatched(self, dbmatched: str) -> None:
        """
        write database sequences with hits to file.

        Args:
            dbmatched (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"dbmatched": dbmatched})
    def set_dbnotmatched(self, dbnotmatched: str) -> None:
        """
        write database sequences with no hits to file.

        Args:
            dbnotmatched (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"dbnotmatched": dbnotmatched})
    
    def set_blast6out(self, blast6out: str) -> None:
        """
        write BLAST6 output to file.

        Args:
            blast6out (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"blast6out": blast6out})

class TaxonomyClassification(Vsearch):
    """
    A sub class of Vsearch specific for taxonomy classification
    """

    def __init__(self, config: Config):
        """
        Initialize the TaxonomyClassification with a configuration object.

        :param config: Configuration object containing tool and logger settings.
        :type config: Config
        """
        super().__init__(config)

    def set_sintax(self, sintax: str) -> None:
        """
        set filename of queries for sintax.

        Args:
            sintax (str): The path to the input fasta/fastq
        
        Returns:
            None        
        """
        assert os.path.exists(sintax), f"Input  file not found: {sintax}"
        self.set_params({"sintax": sintax})
    
    def set_sintax_cutoff(self, sintax_cutoff: float) -> None:
        """
        set confidence value cutoff level (default 0.0).

        Args:
            sintax_cutoff (float): Sintax cutoff for taxonomic assignment.
        
        Returns:
            None        
        """
        self.set_params({"sintax_cutoff": str(sintax_cutoff)})
    
    def set_tabbedout(self, tabbedout: str) -> None:
        """
        write results to given tab-delimited file.

        Args:
            tabbedout (str): The path to the output file.
        
        Returns:
            None        
        """
        self.set_params({"tabbedout": tabbedout})